from __future__ import annotations
from typing import Tuple, List, Optional
from compiler.ast_nodes import *
from compiler.diagnostics import Diagnostic
from utils.symbols import SymbolTable, Symbol
from compiler.ast_nodes import *
from compiler.ast_nodes import Literal as LiteralExpr

# --------- Utilidades de tipos ---------
NUMERIC = {"int", "double"}

def common_numeric(a: str, b: str) -> Optional[str]:
    if a in NUMERIC and b in NUMERIC:
        return "double" if ("double" in (a, b)) else "int"
    return None

def can_assign(dst: str, src: str) -> bool:
    if dst == src: return True
    # widening int -> double
    if dst == "double" and src == "int": return True
    return False

# --------- Analizador semántico ---------
class SemAnalyzer:
    def __init__(self):
        self.diags: List[Diagnostic] = []
        self.symtab = SymbolTable()
        self.current_return_type: Optional[TypeRef] = None  # Tipo de retorno del método actual
        self.loop_depth: int = 0  # Contador de loops anidados (para validar break/continue)

    def analyze(self, cu: CompilationUnit) -> Tuple[CompilationUnit, List[Diagnostic], SymbolTable]:
        # nivel clase
        cls = cu.class_decl
        # Definir símbolo de clase
        self.symtab.define(Symbol(cls.name, TypeRef("void"), cls.span, "class"))

        self.symtab.enter()  # ámbito clase
        for m in cls.methods:
            # Declaración de método con información de parámetros
            param_types = [(p.type, p.name) for p in m.params]
            metadata = {
                'params': param_types,
                'arity': len(m.params)
            }
            ok = self.symtab.define(Symbol(m.name, m.return_type, m.span, "method", metadata))
            if not ok:
                self._error(m.span, "SEM_REDEF", f"Método redefinido: {m.name}", stage="semantics")

        for m in cls.methods:
            self._check_method(m)

        # salir del ámbito de clase
        scope, usage = self.symtab.exit()
        # (nada que reportar a nivel clase por 'unused')

        return cu, self.diags, self.symtab

    # --------- Métodos ---------
    def _check_method(self, m: MethodDecl):
        # nuevo ámbito método
        self.symtab.enter()
        
        # Guardar el tipo de retorno actual
        self.current_return_type = m.return_type

        # parámetros
        for p in m.params:
            if not self.symtab.define(Symbol(p.name, p.type, p.span, "param")):
                self._error(p.span, "SEM_REDEF", f"Parámetro redefinido: {p.name}", "semantics")

        # cuerpo
        self._check_stmt(m.body)
        
        # Restaurar
        self.current_return_type = None

        # warnings: parámetros no usados
        scope, usage = self.symtab.exit()
        for name in [n for n, used in usage.items() if not used]:
            sym = scope[name]
            self._warn(sym.span, "SEM_UNUSED", f"Símbolo no usado: {name}", "semantics")

    # --------- Sentencias ---------
    def _check_stmt(self, s: Stmt):
        if isinstance(s, Block):
            self.symtab.enter()
            for st in s.stmts:
                self._check_stmt(st)
            scope, usage = self.symtab.exit()
            for name in [n for n, used in usage.items() if not used]:
                sym = scope[name]
                self._warn(sym.span, "SEM_UNUSED", f"Variable no usada: {name}", "semantics")

        elif isinstance(s, VarDecl):
            # shadowing o redefinición
            existing_cur = self.symtab.resolve_in_current(s.name)
            if existing_cur is not None:
                self._error(s.span, "SEM_REDEF", f"Variable ya definida en este ámbito: {s.name}", "semantics")
            else:
                existing_outer = self.symtab.resolve(s.name)
                if existing_outer is not None:
                    self._warn(s.span, "SEM_SHADOW", f"Sombras variable de ámbito externo: {s.name}", "semantics")
                self.symtab.define(Symbol(s.name, s.type, s.span, "var"))

            if s.init is not None:
                et = self._check_expr(s.init)
                if not can_assign(s.type.kind, et.kind):
                    self._error(s.span, "SEM_ASSIGN", f"No se puede asignar {et.kind} a {s.type.kind}", "semantics")

        elif isinstance(s, ExprStmt):
            self._check_expr(s.expr)

        elif isinstance(s, If):
            ct = self._check_expr(s.cond)
            if ct.kind != "boolean":
                self._error(s.span, "SEM_COND", "La condición de if debe ser boolean", "semantics")
            self._check_stmt(s.then_branch)
            if s.else_branch:
                self._check_stmt(s.else_branch)

        elif isinstance(s, While):
            ct = self._check_expr(s.cond)
            if ct.kind != "boolean":
                self._error(s.span, "SEM_COND", "La condición de while debe ser boolean", "semantics")
            self.loop_depth += 1
            self._check_stmt(s.body)
            self.loop_depth -= 1

        elif isinstance(s, For):
            # init son Stmt (var decl o expr;)
            for st in s.init:
                self._check_stmt(st)
            if s.cond is not None:
                ct = self._check_expr(s.cond)
                if ct.kind != "boolean":
                    self._error(s.span, "SEM_COND", "La condición de for debe ser boolean", "semantics")
            for e in s.step:
                self._check_expr(e)
            self.loop_depth += 1
            self._check_stmt(s.body)
            self.loop_depth -= 1

        elif isinstance(s, Return):
            # Validar que estemos en un método
            if self.current_return_type is None:
                self._error(s.span, "SEM_RETURN", "Return fuera de método", "semantics")
                return
            
            # Validar el tipo de retorno
            if s.value is None:
                # return sin valor
                if self.current_return_type.kind != "void":
                    self._error(s.span, "SEM_RETURN", 
                               f"Método de tipo {self.current_return_type.kind} debe retornar un valor", 
                               "semantics")
            else:
                # return con valor
                if self.current_return_type.kind == "void":
                    self._error(s.span, "SEM_RETURN", 
                               "Método void no debe retornar un valor", 
                               "semantics")
                else:
                    ret_type = self._check_expr(s.value)
                    if not can_assign(self.current_return_type.kind, ret_type.kind):
                        self._error(s.span, "SEM_RETURN", 
                                   f"No se puede retornar {ret_type.kind} en método de tipo {self.current_return_type.kind}", 
                                   "semantics")

        elif isinstance(s, Break):
            if self.loop_depth == 0:
                self._error(s.span, "SEM_BREAK", "break fuera de un loop", "semantics")

        elif isinstance(s, Continue):
            if self.loop_depth == 0:
                self._error(s.span, "SEM_CONTINUE", "continue fuera de un loop", "semantics")

        else:
            # otros nodos no contemplados en v1
            pass

    # --------- Expresiones ---------
    def _check_expr(self, e: Expr) -> TypeRef:
        if isinstance(e, Literal):
            return e.type

        if isinstance(e, Ident):
            sym = self.symtab.resolve(e.name)
            if sym is None:
                self._error(e.span, "SEM_UNDECL", f"Identificador no declarado: {e.name}", "semantics")
                return TypeRef("int")
            # marcar uso
            self.symtab.mark_used(e.name)
            return sym.type

        if isinstance(e, Assign):
            lt = self._check_expr(e.target)
            rt = self._check_expr(e.value)
            # Permitimos asignar a Ident o ArrayAccess
            if not isinstance(e.target, (Ident, ArrayAccess)):
                self._error(e.span, "SEM_LVALUE", "Lado izquierdo de asignación debe ser una variable o acceso a array", "semantics")
            if not can_assign(lt.kind, rt.kind):
                self._error(e.span, "SEM_ASSIGN", f"No se puede asignar {rt.kind} a {lt.kind}", "semantics")
            return lt

        if isinstance(e, Unary):
            t = self._check_expr(e.operand)
            if e.op == "!":
                if t.kind != "boolean":
                    self._error(e.span, "SEM_TYPE", "Operador ! requiere boolean", "semantics")
                return TypeRef("boolean")
            if e.op == "-":
                if t.kind not in NUMERIC:
                    self._error(e.span, "SEM_TYPE", "Operador unario '-' requiere tipo numérico", "semantics")
                return t
            return t

        if isinstance(e, Binary):
            lt = self._check_expr(e.left)
            rt = self._check_expr(e.right)
            op = e.op

            if op in {"+","-","*","/","%"}:
                k = common_numeric(lt.kind, rt.kind)
                if k is None:
                    self._error(e.span, "SEM_TYPE", f"Operador {op} requiere tipos numéricos", "semantics")
                    return TypeRef("int")
                return TypeRef(k)

            if op in {"<","<=",">",">="}:
                k = common_numeric(lt.kind, rt.kind)
                if k is None:
                    self._error(e.span, "SEM_TYPE", f"Operador {op} requiere tipos numéricos", "semantics")
                return TypeRef("boolean")

            if op in {"==","!="}:
                # permitimos comparar mismos tipos o mezcla numérica
                if lt.kind == rt.kind or common_numeric(lt.kind, rt.kind) is not None:
                    return TypeRef("boolean")
                self._error(e.span, "SEM_TYPE", f"No se pueden comparar {lt.kind} y {rt.kind}", "semantics")
                return TypeRef("boolean")

            if op in {"&&","||"}:
                if lt.kind != "boolean" or rt.kind != "boolean":
                    self._error(e.span, "SEM_TYPE", f"Operador {op} requiere booleanos", "semantics")
                return TypeRef("boolean")

            # op no reconocido
            return lt

        if isinstance(e, Select):
            # select a.b — su tipo se decide por casos especiales (System.out)
            # Devolvemos tipo ficticio para permitir chain hasta println
            return TypeRef("void")

        if isinstance(e, Call):
            # reconocimiento de System.out.println(...)
            if self._is_system_out_println(e.callee):
                # v1: aridad 1
                if len(e.args) != 1:
                    self._error(e.span, "SEM_ARGC", f"println espera 1 argumento, recibió {len(e.args)}", "semantics")
                else:
                    self._check_expr(e.args[0])  # acepta cualquier tipo soportado
                return TypeRef("void")
            
            # Llamadas a métodos propios (simple: nombre(args))
            if isinstance(e.callee, Ident):
                method_name = e.callee.name
                method_sym = self.symtab.resolve(method_name)
                
                if method_sym is None:
                    self._error(e.span, "SEM_UNDECL", f"Método no declarado: {method_name}", "semantics")
                    return TypeRef("void")
                
                if method_sym.kind != "method":
                    self._error(e.span, "SEM_CALL", f"{method_name} no es un método", "semantics")
                    return TypeRef("void")
                
                # Marcar uso del método
                self.symtab.mark_used(method_name)
                
                # Validar aridad
                if method_sym.metadata:
                    expected_arity = method_sym.metadata.get('arity', 0)
                    actual_arity = len(e.args)
                    
                    if expected_arity != actual_arity:
                        self._error(e.span, "SEM_ARGC", 
                                   f"Método {method_name} espera {expected_arity} argumento(s), recibió {actual_arity}", 
                                   "semantics")
                    
                    # Validar tipos de argumentos
                    param_types = method_sym.metadata.get('params', [])
                    for i, arg in enumerate(e.args):
                        arg_type = self._check_expr(arg)
                        if i < len(param_types):
                            expected_type = param_types[i][0]  # (TypeRef, name)
                            if not can_assign(expected_type.kind, arg_type.kind):
                                self._error(e.span, "SEM_ARGTYPE", 
                                           f"Argumento {i+1} de {method_name}: esperado {expected_type.kind}, recibido {arg_type.kind}", 
                                           "semantics")
                else:
                    # Sin metadata, solo chequeamos las expresiones
                    for arg in e.args:
                        self._check_expr(arg)
                
                return method_sym.type
            
            # otros llamados (no soportados)
            self._error(e.span, "SEM_CALL", "Llamadas a métodos complejos no soportadas", "semantics")
            return TypeRef("void")

        if isinstance(e, NewArray):
            # new int[size] o new int[]{...}
            if e.size is not None:
                # new int[size]
                size_type = self._check_expr(e.size)
                if size_type.kind != "int":
                    self._error(e.span, "SEM_ARRAY", "Tamaño de array debe ser int", "semantics")
            elif e.initializer is not None:
                # new int[]{1,2,3}
                for elem in e.initializer:
                    elem_type = self._check_expr(elem)
                    if not can_assign(e.element_type.kind, elem_type.kind):
                        self._error(e.span, "SEM_ARRAY", 
                                   f"Elemento de tipo {elem_type.kind} no compatible con array de {e.element_type.kind}", 
                                   "semantics")
            # Retorna tipo array
            return TypeRef(e.element_type.kind + "[]")

        if isinstance(e, ArrayAccess):
            # arr[index]
            array_type = self._check_expr(e.array)
            index_type = self._check_expr(e.index)
            
            # Validar que el índice sea int
            if index_type.kind != "int":
                self._error(e.span, "SEM_ARRAY", "Índice de array debe ser int", "semantics")
            
            # Validar que sea un array
            if not array_type.kind.endswith("[]"):
                self._error(e.span, "SEM_ARRAY", f"{array_type.kind} no es un array", "semantics")
                return TypeRef("int")
            
            # Retorna tipo del elemento (quita un nivel de [])
            elem_kind = array_type.kind[:-2]  # quita "[]"
            return TypeRef(elem_kind)

        # fallback
        return TypeRef("int")

    # --------- Helpers ---------
    def _is_system_out_println(self, callee: Expr) -> bool:
        # debe ser Select(Select(Ident('System'), 'out'), 'println')
        if not isinstance(callee, Select): return False
        if callee.name != "println": return False
        recv = callee.receiver
        if not isinstance(recv, Select): return False
        if recv.name != "out": return False
        base = recv.receiver
        return isinstance(base, Ident) and base.name == "System"

    # --------- Diags ---------
    def _error(self, span: Span, code: str, msg: str, stage: str):
        self.diags.append(Diagnostic("error", stage, msg, span.line, span.col, span.end_line, span.end_col, code))

    def _warn(self, span: Span, code: str, msg: str, stage: str):
        self.diags.append(Diagnostic("warning", stage, msg, span.line, span.col, span.end_line, span.end_col, code))

# --------- API pública ---------
def analyze(ast: CompilationUnit) -> Tuple[CompilationUnit, List[Diagnostic], SymbolTable]:
    """
    Chequea tipos/alcances y emite diagnósticos.
    Devuelve el mismo AST, la lista de diagnósticos y la tabla de símbolos raíz.
    """
    return SemAnalyzer().analyze(ast)
