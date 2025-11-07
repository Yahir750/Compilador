from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal, Tuple

# ---------- Tipos y posiciones ----------
@dataclass(frozen=True)
class Span:
    line: int
    col: int
    end_line: int
    end_col: int

TypeKind = Literal["int","double","boolean","String","void"]

@dataclass(frozen=True)
class TypeRef:
    kind: TypeKind

# ---------- Base ----------
class Expr: ...
class Stmt: ...

# ---------- Declaraciones ----------
@dataclass(frozen=True)
class CompilationUnit:
    class_decl: "ClassDecl"

@dataclass(frozen=True)
class ClassDecl:
    name: str
    methods: Tuple["MethodDecl", ...]
    span: Span

@dataclass(frozen=True)
class Param:
    type: TypeRef
    name: str
    span: Span

@dataclass(frozen=True)
class MethodDecl:
    name: str
    return_type: TypeRef
    params: Tuple[Param, ...]
    body: "Block"
    modifiers: Tuple[str, ...]
    span: Span

# ---------- Sentencias ----------
@dataclass(frozen=True)
class Block(Stmt):
    stmts: Tuple[Stmt, ...]
    span: Span

@dataclass(frozen=True)
class VarDecl(Stmt):
    type: TypeRef
    name: str
    init: Optional[Expr]
    span: Span

@dataclass(frozen=True)
class ExprStmt(Stmt):
    expr: Expr
    span: Span

@dataclass(frozen=True)
class If(Stmt):
    cond: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]
    span: Span

@dataclass(frozen=True)
class While(Stmt):
    cond: Expr
    body: Stmt
    span: Span

@dataclass(frozen=True)
class For(Stmt):
    init: Tuple[Stmt, ...]
    cond: Optional[Expr]
    step: Tuple[Expr, ...]
    body: Stmt
    span: Span

# ---------- Expresiones ----------
@dataclass(frozen=True)
class Assign(Expr):
    target: Expr
    value: Expr
    span: Span

@dataclass(frozen=True)
class Binary(Expr):
    op: str
    left: Expr
    right: Expr
    span: Span

@dataclass(frozen=True)
class Unary(Expr):
    op: str
    operand: Expr
    span: Span

@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    args: Tuple[Expr, ...]
    span: Span

@dataclass(frozen=True)
class Select(Expr):
    receiver: Expr
    name: str
    span: Span

@dataclass(frozen=True)
class Ident(Expr):
    name: str
    span: Span

@dataclass(frozen=True)
class Literal(Expr):
    value: object
    type: TypeRef
    span: Span
