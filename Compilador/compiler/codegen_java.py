from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Union

from compiler.diagnostics import Diagnostic
from compiler.ast_nodes import (
    CompilationUnit, ClassDecl, MethodDecl, Block, VarDecl, ExprStmt, If, While, For,
    Assign, Binary, Unary, Call, Select, Ident, Literal as LiteralExpr, Expr, Stmt,
    TypeRef, Param
)
from compiler.ir import IRProgram  # solo para el type hint del modo "ir"

# -------------------------------------------------
# Utilidades de escritura con sangrías
# -------------------------------------------------
@dataclass
class _Out:
    lines: List[str]
    indent: int = 0
    indent_str: str = "    "  # 4 espacios

    def writeln(self, s: str = "") -> None:
        if s:
            self.lines.append(f"{self.indent_str * self.indent}{s}")
        else:
            self.lines.append("")

    def write(self, s: str) -> None:
        if s:
            if self.lines and self.lines[-1] and not self.lines[-1].endswith("\n"):
                # agrega al final de la línea actual
                self.lines[-1] = f"{self.lines[-1]}{s}"
            else:
                self.lines.append(f"{self.indent_str * self.indent}{s}")

    def join(self) -> str:
        return "\n".join(self.lines)

# -------------------------------------------------
# Emisor principal (AST -> Java)
# -------------------------------------------------
class _EmitJavaAST:
    def __init__(self):
        self.out = _Out([])
        self.diags: List[Diagnostic] = []

    # ---------- API ----------
    def emit(self, cu: CompilationUnit) -> Tuple[str, List[Diagnostic]]:
        self._emit_class(cu.class_decl)
        return self.out.join(), self.diags

    # ---------- Helpers ----------
    def _type_to_java(self, t: TypeRef) -> str:
        return t.kind

    def _emit_class(self, c: ClassDecl) -> None:
        self.out.writeln(f"class {c.name} {{")
        self.out.indent += 1
        for m in c.methods:
            self._emit_method(m)
            self.out.writeln()
        self.out.indent -= 1
        self.out.writeln("}")

    def _emit_method(self, m: MethodDecl) -> None:
        mods = " ".join(m.modifiers) + (" " if m.modifiers else "")
        ret = self._type_to_java(m.return_type)
        params = ", ".join(f"{self._type_to_java(p.type)} {p.name}" for p in m.params)
        self.out.writeln(f"{mods}{ret} {m.name}({params}) " + "{")
        self.out.indent += 1
        self._emit_block(m.body, omit_braces=True)
        self.out.indent -= 1
        self.out.writeln("}")

    def _emit_block(self, b: Block, omit_braces: bool = False) -> None:
        if not omit_braces:
            self.out.writeln("{")
            self.out.indent += 1
        for s in b.stmts:
            self._emit_stmt(s)
        if not omit_braces:
            self.out.indent -= 1
            self.out.writeln("}")

    # ---------- Sentencias ----------
    def _emit_stmt(self, s: Stmt) -> None:
        if isinstance(s, Block):
            self._emit_block(s)
            return
        if isinstance(s, VarDecl):
            decl = f"{self._type_to_java(s.type)} {s.name}"
            if s.init is not None:
                decl += f" = {self._expr(s.init)}"
            self.out.writeln(decl + ";")
            return
        if isinstance(s, ExprStmt):
            self.out.writeln(self._expr(s.expr) + ";")
            return
        if isinstance(s, If):
            self.out.writeln(f"if ({self._expr(s.cond)}) " + "{")
            self.out.indent += 1
            self._emit_stmt(s.then_branch)
            self.out.indent -= 1
            if s.else_branch:
                # else en misma línea estilo K&R
                self.out.writeln("} else {")
                self.out.indent += 1
                self._emit_stmt(s.else_branch)
                self.out.indent -= 1
                self.out.writeln("}")
            else:
                self.out.writeln("}")
            return
        if isinstance(s, While):
            self.out.writeln(f"while ({self._expr(s.cond)}) " + "{")
            self.out.indent += 1
            self._emit_stmt(s.body)
            self.out.indent -= 1
            self.out.writeln("}")
            return
        if isinstance(s, For):
            init_str = self._for_init_str(s.init)
            cond_str = self._expr(s.cond) if s.cond is not None else ""
            step_str = ", ".join(self._expr(e) for e in s.step)
            self.out.writeln(f"for ({init_str}; {cond_str}; {step_str}) " + "{")
            self.out.indent += 1
            self._emit_stmt(s.body)
            self.out.indent -= 1
            self.out.writeln("}")
            return
        # fallback: bloque con comentario si algo no reconocido
        self.out.writeln("{ /* unsupported statement in v1 */ }")

    def _for_init_str(self, inits: tuple[Stmt, ...]) -> str:
        """
        v1: soportamos una sola declaración o una sola expresión en init.
        Si hay múltiples, las unimos por coma cuando sean ExprStmt; si es VarDecl, asumimos una.
        """
        if not inits:
            return ""
        if len(inits) == 1:
            s = inits[0]
            if isinstance(s, VarDecl):
                decl = f"{self._type_to_java(s.type)} {s.name}"
                if s.init is not None:
                    decl += f" = {self._expr(s.init)}"
                return decl
            if isinstance(s, ExprStmt):
                return self._expr(s.expr)
            # como fallback, imprime un comentario (no rompe compilación pero no hace nada útil)
            return "/* unsupported for-init */"
        # múltiples
        parts: List[str] = []
        for s in inits:
            if isinstance(s, ExprStmt):
                parts.append(self._expr(s.expr))
            else:
                parts.append("/* unsupported */")
        return ", ".join(parts)

    # ---------- Expresiones ----------
    def _expr(self, e: Expr) -> str:
        if isinstance(e, LiteralExpr):
            # String ya viene con comillas, boolean numéricos los convertimos a literales Java
            if e.type.kind == "boolean":
                return "true" if bool(e.value) else "false"
            if e.type.kind == "String":
                return str(e.value)  # incluye comillas
            if e.type.kind == "double":
                # Representación estable para floats
                return repr(float(e.value))
            # int por defecto
            return str(int(e.value))

        if isinstance(e, Ident):
            return e.name

        if isinstance(e, Assign):
            return f"{self._expr(e.target)} = {self._expr(e.value)}"

        if isinstance(e, Unary):
            # Paréntesis para preservar agrupación si es necesario
            return f"{e.op}{self._paren_if_needed(e.operand)}"

        if isinstance(e, Binary):
            left = self._paren_if_needed(e.left)
            right = self._paren_if_needed(e.right)
            return f"{left} {self._binop_to_java(e.op)} {right}"

        if isinstance(e, Select):
            return f"{self._expr(e.receiver)}.{e.name}"

        if isinstance(e, Call):
            callee = self._expr(e.callee)
            args = ", ".join(self._expr(a) for a in e.args)
            return f"{callee}({args})"

        return "/* unsupported expr */"

    def _binop_to_java(self, op: str) -> str:
        # En nuestro AST guardamos el lexema de operador directamente (p.ej. "+", "==")
        return op

    def _paren_if_needed(self, e: Expr) -> str:
        """Envuelve en paréntesis para mantener precedencia básica en pretty-print."""
        if isinstance(e, (LiteralExpr, Ident, Select, Call)):
            return self._expr(e)
        # Para operaciones compuestas, rodear
        return f"({self._expr(e)})"

# -------------------------------------------------
# Emisor desde IR (placeholder simple)
# -------------------------------------------------
class _EmitJavaIR:
    def __init__(self):
        self.diags: List[Diagnostic] = []

    def emit(self, prog: IRProgram) -> Tuple[str, List[Diagnostic]]:
        # Placeholder que devuelve un archivo Java válido con comentarios del IR,
        # pero no recompone control flow (eso se puede implementar en una fase futura).
        # Nota: El orquestador usa `from_stage="ast"` por defecto, así que esto es opcional en v1.
        lines: List[str] = []
        lines.append("/* codegen from IR no implementado en v1: emitiendo comentarios del IR */")
        lines.append("class Main {")
        for fn in prog.funcs:
            lines.append(f"    static void {fn.name}() {{")
            for bb in fn.blocks:
                lines.append(f"        // {bb.label}")
                for ins in bb.instrs:
                    lines.append(f"        //   {ins}")
            lines.append("    }")
        lines.append("}")
        self.diags.append(Diagnostic(
            severity="info", stage="codegen",
            message="Generación desde IR no implementada en v1; se emitieron comentarios.",
            line=0, col=0, end_line=0, end_col=0, code="CODEGEN_IR_PLACEHOLDER"
        ))
        return "\n".join(lines), self.diags

# -------------------------------------------------
# API pública
# -------------------------------------------------
def emit(node: Union[CompilationUnit, IRProgram], from_stage: str = "ast") -> Tuple[str, List[Diagnostic]]:
    """
    Genera Java (texto) desde AST (v1) o IR (placeholder).
    Retorna (java_src, diagnostics).
    """
    if from_stage == "ir":
        return _EmitJavaIR().emit(node)  # type: ignore[arg-type]
    # por defecto, desde AST
    return _EmitJavaAST().emit(node)     # type: ignore[arg-type]
