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

# Tipos base: "int", "double", "boolean", "String", "void"
# Tipos array: "int[]", "double[]", "boolean[]", "String[]"
# Tipos multidimensionales: "int[][]", etc.
TypeKind = str  # Cambio de Literal a str para soportar arrays

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

@dataclass(frozen=True)
class Return(Stmt):
    value: Optional[Expr]
    span: Span

@dataclass(frozen=True)
class Break(Stmt):
    span: Span

@dataclass(frozen=True)
class Continue(Stmt):
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

@dataclass(frozen=True)
class NewArray(Expr):
    """new int[size] o new int[]{1,2,3}"""
    element_type: TypeRef  # tipo del elemento (sin [])
    size: Optional[Expr]   # tamaño si es new int[10], None si es inicializador
    initializer: Optional[Tuple[Expr, ...]]  # elementos si es new int[]{1,2,3}
    span: Span

@dataclass(frozen=True)
class ArrayAccess(Expr):
    """arr[index]"""
    array: Expr
    index: Expr
    span: Span
