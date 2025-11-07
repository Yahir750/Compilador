from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Literal as TypingLiteral
from compiler.ast_nodes import (
    CompilationUnit, ClassDecl, MethodDecl, Block, VarDecl, ExprStmt, If, While, For,
    Assign, Binary, Unary, Call, Select, Ident, Literal as LiteralExpr, Expr, Stmt, TypeRef, Span
)
from compiler.diagnostics import Diagnostic

# ========== Instrucciones IR ==========

@dataclass(frozen=True)
class Instr:
    span: Optional[Span] = None

@dataclass(frozen=True)
class LABEL(Instr):
    name: str = ""

@dataclass(frozen=True)
class JUMP(Instr):
    target: str = ""

@dataclass(frozen=True)
class CJUMP(Instr):
    cond: str = ""
    if_true: str = ""
    if_false: str = ""

@dataclass(frozen=True)
class MOVE(Instr):
    dst: str = ""
    src: str = ""

@dataclass(frozen=True)
class BINOP(Instr):
    op: TypingLiteral["ADD","SUB","MUL","DIV","MOD"] = "ADD"
    dst: str = ""
    a: str = ""
    b: str = ""

@dataclass(frozen=True)
class CMP(Instr):
    dst: str = ""
    a: str = ""
    op: TypingLiteral["==","!=", "<", "<=", ">", ">="] = "=="
    b: str = ""

@dataclass(frozen=True)
class CALL(Instr):
    dst: Optional[str] = None
    name: str = ""
    args: Tuple[str, ...] = ()

@dataclass(frozen=True)
class RET(Instr):
    value: Optional[str] = None

# ========== CFG ==========

@dataclass(frozen=True)
class BasicBlock:
    label: str
    instrs: Tuple[Instr, ...]

@dataclass(frozen=True)
class IRFunc:
    name: str
    params: Tuple[str, ...]
    blocks: Tuple[BasicBlock, ...]
    temps: int

@dataclass(frozen=True)
class IRProgram:
    funcs: Tuple[IRFunc, ...]

# ========== Lowering (AST -> IR) ==========

class Lowerer:
    def __init__(self):
        self.diags: List[Diagnostic] = []
        self.blocks: List[List[Instr]] = []
        self.cur_label_idx = 0
        self.temp_idx = 0
        self.cur_block_name = ""
        self.funcs: List[IRFunc] = []
        self.loop_stack: List[Dict[str, str]] = []
        self.env_scopes: List[Dict[str, TypeRef]] = []

    def new_temp(self) -> str:
        self.temp_idx += 1
        return f"t{self.temp_idx}"

    def new_label(self, base: str = "L") -> str:
        self.cur_label_idx += 1
        return f"{base}{self.cur_label_idx}"

    def start_block(self, label: Optional[str] = None):
        if label is None:
            label = self.new_label("L")
        self.cur_block_name = label
        self.blocks.append([LABEL(name=label)])

    def emit(self, instr: Instr):
        if not self.blocks:
            self.start_block(self.new_label("entry"))
        self.blocks[-1].append(instr)

    def close_blocks(self) -> Tuple[BasicBlock, ...]:
        bbs: List[BasicBlock] = []
        for lst in self.blocks:
            if not lst or not isinstance(lst[0], LABEL):
                lbl = self.new_label("Lfix")
                lst.insert(0, LABEL(name=lbl))
            label = lst[0].name
            bbs.append(BasicBlock(label, tuple(lst)))
        return tuple(bbs)

    def push_env(self):
        self.env_scopes.append({})

    def pop_env(self):
        self.env_scopes.pop()

    def define_var(self, name: str, typ: TypeRef):
        if not self.env_scopes:
            self.push_env()
        self.env_scopes[-1][name] = typ

    def resolve_var(self, name: str) -> Optional[TypeRef]:
        for scope in reversed(self.env_scopes):
            if name in scope:
                return scope[name]
        return None

    def lower(self, cu: CompilationUnit) -> Tuple[IRProgram, List[Diagnostic]]:
        self.funcs.clear()
        self.diags.clear()

        cls: ClassDecl = cu.class_decl

        for m in cls.methods:
            self.temp_idx = 0
            self.cur_label_idx = 0
            self.blocks = []
            self.env_scopes = []
            self.start_block(self.new_label(f"{m.name}_entry"))
            self.push_env()

            for p in m.params:
                self.define_var(p.name, p.type)

            self.lower_stmt(m.body)
            self.emit(RET())

            blocks = self.close_blocks()
            fn = IRFunc(
                name=m.name,
                params=tuple(p.name for p in m.params),
                blocks=blocks,
                temps=self.temp_idx
            )
            self.funcs.append(fn)
            self.pop_env()

        prog = IRProgram(tuple(self.funcs))
        return prog, self.diags

    def lower_stmt(self, s: Stmt):
        if isinstance(s, Block):
            self.push_env()
            for st in s.stmts:
                self.lower_stmt(st)
            self.pop_env()
            return

        if isinstance(s, VarDecl):
            self.define_var(s.name, s.type)
            if s.init is not None:
                val = self.lower_expr(s.init)
                self.emit(MOVE(dst=s.name, src=val, span=s.span))
            return

        if isinstance(s, ExprStmt):
            _ = self.lower_expr(s.expr)
            return

        if isinstance(s, If):
            l_true = self.new_label("if_true_")
            l_false = self.new_label("if_false_")
            l_end = self.new_label("if_end_")

            cond_val = self.lower_cond_as_temp(s.cond)
            self.emit(CJUMP(cond=cond_val, if_true=l_true, if_false=l_false, span=s.span))

            self.start_block(l_true)
            self.lower_stmt(s.then_branch)
            self.emit(JUMP(target=l_end))

            self.start_block(l_false)
            if s.else_branch:
                self.lower_stmt(s.else_branch)
            self.emit(JUMP(target=l_end))

            self.start_block(l_end)
            return

        if isinstance(s, While):
            l_test = self.new_label("while_test_")
            l_body = self.new_label("while_body_")
            l_end = self.new_label("while_end_")

            self.emit(JUMP(target=l_test))
            self.start_block(l_test)
            cond_val = self.lower_cond_as_temp(s.cond)
            self.emit(CJUMP(cond=cond_val, if_true=l_body, if_false=l_end, span=s.span))

            self.start_block(l_body)
            self.lower_stmt(s.body)
            self.emit(JUMP(target=l_test))

            self.start_block(l_end)
            return

        if isinstance(s, For):
            for st in s.init:
                self.lower_stmt(st)

            l_test = self.new_label("for_test_")
            l_body = self.new_label("for_body_")
            l_step = self.new_label("for_step_")
            l_end = self.new_label("for_end_")

            self.emit(JUMP(target=l_test))

            self.start_block(l_test)
            if s.cond is not None:
                cond_val = self.lower_cond_as_temp(s.cond)
                self.emit(CJUMP(cond=cond_val, if_true=l_body, if_false=l_end, span=s.span))
            else:
                self.emit(JUMP(target=l_body))

            self.start_block(l_body)
            self.lower_stmt(s.body)
            self.emit(JUMP(target=l_step))

            self.start_block(l_step)
            for e in s.step:
                _ = self.lower_expr(e)
            self.emit(JUMP(target=l_test))

            self.start_block(l_end)
            return

        return

    def lower_expr(self, e: Expr) -> str:
        if isinstance(e, LiteralExpr):
            return self._imm_of_literal(e)

        if isinstance(e, Ident):
            typ = self.resolve_var(e.name)
            if typ is None:
                self.diags.append(Diagnostic("error","ir",f"Uso de identificador no declarado: {e.name}",
                                             e.span.line,e.span.col,e.span.end_line,e.span.end_col,"IR_UNDECL"))
            return e.name

        if isinstance(e, Assign):
            rhs = self.lower_expr(e.value)
            if isinstance(e.target, Ident):
                self.emit(MOVE(dst=e.target.name, src=rhs, span=e.span))
                return e.target.name
            else:
                t = self.new_temp()
                self.emit(MOVE(dst=t, src=rhs, span=e.span))
                return t

        if isinstance(e, Unary):
            v = self.lower_expr(e.operand)
            if e.op == "-":
                t = self.new_temp()
                self.emit(BINOP(op="SUB", dst=t, a="#0", b=v, span=e.span))
                return t
            if e.op == "!":
                # !x  ->  (x == 0)  (boole 1/0 en CMP)
                t = self.new_temp()
                self.emit(CMP(dst=t, a=v, op="==", b="#0", span=e.span))
                return t
            return v

        if isinstance(e, Binary):
            if e.op in {"+","-","*","/","%"}:
                a = self.lower_expr(e.left)
                b = self.lower_expr(e.right)
                t = self.new_temp()
                mapping = {"+":"ADD","-":"SUB","*":"MUL","/":"DIV","%":"MOD"}
                self.emit(BINOP(op=mapping[e.op], dst=t, a=a, b=b, span=e.span))
                return t

            if e.op in {"<","<=",">",">=","==","!="}:
                a = self.lower_expr(e.left)
                b = self.lower_expr(e.right)
                t = self.new_temp()
                self.emit(CMP(dst=t, a=a, op=e.op, b=b, span=e.span))
                return t

            if e.op in {"&&","||"}:
                if e.op == "&&":
                    return self._lower_sc_and(e)
                else:
                    return self._lower_sc_or(e)

        if isinstance(e, Select):
            if isinstance(e.receiver, Ident) and e.receiver.name == "System" and e.name == "out":
                return "System.out"
            if isinstance(e.receiver, Select) and e.receiver.name == "out" and isinstance(e.receiver.receiver, Ident) and e.name == "println":
                return "System.out.println"
            t = self.new_temp()
            self.emit(MOVE(dst=t, src=f"{self._as_str(self.lower_expr(e.receiver))}.{e.name}", span=e.span))
            return t

        if isinstance(e, Call):
            callee_name = self._as_str(self.lower_expr(e.callee))
            args_vals = tuple(self.lower_expr(a) for a in e.args)
            if callee_name.endswith("System.out.println"):
                self.emit(CALL(dst=None, name="println", args=args_vals, span=e.span))
                t = self.new_temp()
                self.emit(MOVE(dst=t, src="#0", span=e.span))
                return t
            self.diags.append(Diagnostic("error","ir","Llamada no soportada en v1",
                                         e.span.line,e.span.col,e.span.end_line,e.span.end_col,"IR_CALL"))
            t = self.new_temp()
            self.emit(MOVE(dst=t, src="#0", span=e.span))
            return t

        t = self.new_temp()
        self.emit(MOVE(dst=t, src="#0", span=getattr(e, "span", None)))
        return t

    def lower_cond_as_temp(self, cond: Expr) -> str:
        if isinstance(cond, Binary) and cond.op in {"&&","||"}:
            if cond.op == "&&":
                return self._lower_sc_and(cond)
            else:
                return self._lower_sc_or(cond)
        v = self.lower_expr(cond)
        t = self.new_temp()
        self.emit(CMP(dst=t, a=v, op="!=", b="#0", span=cond.span))
        return t

    def _lower_sc_and(self, e: Binary) -> str:
        t = self.new_temp()
        self.emit(MOVE(dst=t, src="#0", span=e.span))
        l_true = self.new_label("and_true_")
        l_end = self.new_label("and_end_")

        lv = self.lower_expr(e.left)
        ltmp = self.new_temp()
        self.emit(CMP(dst=ltmp, a=lv, op="!=", b="#0", span=e.span))
        self.emit(CJUMP(cond=ltmp, if_true=l_true, if_false=l_end, span=e.span))

        self.start_block(l_true)
        rv = self.lower_expr(e.right)
        rtmp = self.new_temp()
        self.emit(CMP(dst=rtmp, a=rv, op="!=", b="#0", span=e.span))
        self.emit(MOVE(dst=t, src=rtmp, span=e.span))
        self.emit(JUMP(target=l_end))

        self.start_block(l_end)
        return t

    def _lower_sc_or(self, e: Binary) -> str:
        t = self.new_temp()
        self.emit(MOVE(dst=t, src="#1", span=e.span))
        l_false = self.new_label("or_false_")
        l_end = self.new_label("or_end_")

        lv = self.lower_expr(e.left)
        ltmp = self.new_temp()
        self.emit(CMP(dst=ltmp, a=lv, op="!=", b="#0", span=e.span))
        self.emit(CJUMP(cond=ltmp, if_true=l_end, if_false=l_false, span=e.span))

        self.start_block(l_false)
        rv = self.lower_expr(e.right)
        rtmp = self.new_temp()
        self.emit(CMP(dst=rtmp, a=rv, op="!=", b="#0", span=e.span))
        self.emit(MOVE(dst=t, src=rtmp, span=e.span))
        self.emit(JUMP(target=l_end))

        self.start_block(l_end)
        return t

    def _imm_of_literal(self, lit: LiteralExpr) -> str:
        if lit.type.kind == "int":
            return f"#{int(lit.value)}"
        if lit.type.kind == "double":
            return f"#{float(lit.value)}"
        if lit.type.kind == "boolean":
            return "#1" if bool(lit.value) else "#0"
        if lit.type.kind == "String":
            return str(lit.value)
        return "#0"

    def _as_str(self, v: str) -> str:
        return v

def lower(ast: CompilationUnit) -> tuple[IRProgram, list[Diagnostic]]:
    return Lowerer().lower(ast)
