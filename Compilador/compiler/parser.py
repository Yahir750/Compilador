from __future__ import annotations
from typing import List, Tuple, Optional
from utils.tokens import Token
from compiler.ast_nodes import *
from compiler.diagnostics import Diagnostic

def _span_of(tok: Token) -> Span:
    return Span(tok.line, tok.col, tok.end_line, tok.end_col)

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0
        self.n = len(tokens)
        self.diags: List[Diagnostic] = []

    def peek(self, off: int = 0) -> Token:
        j = self.i + off
        return self.tokens[j] if j < self.n else self.tokens[-1]

    def match(self, kind: str) -> Optional[Token]:
        if self.peek().kind == kind:
            t = self.peek()
            self.i += 1
            return t
        return None

    def expect(self, kind: str, msg: str):
        tok = self.peek()
        if tok.kind == kind:
            self.i += 1
            return tok
        self.diags.append(Diagnostic(
            "error", "parser", f"Se esperaba {msg}",
            tok.line, tok.col, tok.end_line, tok.end_col, "PAR001"
        ))
        return tok

    # ---------- Entrada ----------
    def parse(self) -> Tuple[CompilationUnit, List[Diagnostic]]:
        cls = self.class_decl()
        return CompilationUnit(cls), self.diags

    # ---------- Clases y métodos ----------
    def class_decl(self) -> ClassDecl:
        # Permitir 'public' opcional antes de 'class'
        self.match("PUBLIC")

        self.expect("CLASS", "'class'")
        name_tok = self.expect("IDENT", "nombre de clase")
        lbrace = self.expect("LBRACE", "'{'")

        methods: List[MethodDecl] = []
        while self.peek().kind not in {"RBRACE", "EOF"}:
            methods.append(self.method_decl())

        rbrace = self.expect("RBRACE", "'}'")

        return ClassDecl(
            name_tok.lexeme,
            tuple(methods),
            Span(lbrace.line, lbrace.col, rbrace.end_line, rbrace.end_col)
        )

    def method_decl(self) -> MethodDecl:
        mods: List[str] = []
        # Aceptar 'public' opcional
        if self.match("PUBLIC"):
            mods.append("public")
        # Aceptar 'static' opcional (en v1 asumimos métodos estáticos)
        if self.match("STATIC"):
            mods.append("static")

        ret_type = self.type_ref()
        name_tok = self.expect("IDENT", "nombre de método")

        # Argumentos del método
        self.expect("LPAREN", "'('")
        params: List[Param] = []
        if self.peek().kind != "RPAREN":
            params.append(self.param())
            while self.match("COMMA"):
                params.append(self.param())
        self.expect("RPAREN", "')'")

        body = self.block()
        return MethodDecl(
            name_tok.lexeme,
            ret_type,
            tuple(params),
            body,
            tuple(mods),
            _span_of(name_tok)
        )

    def param(self) -> Param:
        t = self.type_ref()
        name_tok = self.expect("IDENT", "identificador de parámetro")
        return Param(t, name_tok.lexeme, _span_of(name_tok))

    def type_ref(self) -> TypeRef:
        t = self.peek()
        if t.kind in {"INT_T", "DOUBLE_T", "BOOLEAN_T", "STRING_T", "VOID"}:
            self.i += 1
            mapping = {
                "INT_T": "int", "DOUBLE_T": "double", "BOOLEAN_T": "boolean",
                "STRING_T": "String", "VOID": "void"
            }
            base = mapping[t.kind]
            # Soporte para arreglos tipo String[] o int[]
            if self.peek().kind == "LBRACK":
                self.i += 1
                self.expect("RBRACK", "']'")
                return TypeRef(base + "[]")
            return TypeRef(base)

        self.diags.append(Diagnostic(
            "error", "parser", "Tipo esperado",
            t.line, t.col, t.end_line, t.end_col, "PAR002"
        ))
        return TypeRef("int")

    # ---------- Bloques y sentencias ----------
    def block(self) -> Block:
        lbrace = self.expect("LBRACE", "'{'")
        stmts: List[Stmt] = []
        while self.peek().kind not in {"RBRACE", "EOF"}:
            s = self.stmt()
            # Si var_decl devolvió lista (múltiples declaraciones), expandimos
            if isinstance(s, list):
                stmts.extend(s)  # cada VarDecl es un Stmt
            else:
                stmts.append(s)
        rbrace = self.expect("RBRACE", "'}'")
        return Block(tuple(stmts), Span(lbrace.line, lbrace.col, rbrace.end_line, rbrace.end_col))

    def stmt(self) -> Stmt | List[Stmt]:
        k = self.peek().kind
        if k in {"INT_T", "DOUBLE_T", "BOOLEAN_T", "STRING_T"}:
            return self.var_decl()  # puede devolver list
        if k == "IF":
            return self.if_stmt()
        if k == "WHILE":
            return self.while_stmt()
        if k == "FOR":
            return self.for_stmt()
        if k == "RETURN":
            return self.return_stmt()
        if k == "LBRACE":
            return self.block()
        # Expresión seguida de ';'
        e = self.expr()
        self.expect("SEMI", "';'")
        return ExprStmt(e, e.span)

    def var_decl(self) -> List[VarDecl] | VarDecl:
        """Soporta múltiples declaraciones en una sola línea: int a=1, b=2;"""
        t = self.type_ref()
        decls: List[VarDecl] = []

        while True:
            name_tok = self.expect("IDENT", "nombre de variable")
            init = None
            if self.match("EQ"):
                init = self.expr()
            decls.append(VarDecl(t, name_tok.lexeme, init, _span_of(name_tok)))

            # Si hay coma, sigue leyendo más variables
            if not self.match("COMMA"):
                break

        self.expect("SEMI", "';'")
        return decls if len(decls) > 1 else decls[0]

    def if_stmt(self) -> If:
        tok = self.expect("IF", "'if'")
        self.expect("LPAREN", "'('")
        cond = self.expr()
        self.expect("RPAREN", "')'")
        then_branch = self.stmt()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.stmt()
        return If(cond, then_branch, else_branch, _span_of(tok))

    def while_stmt(self) -> While:
        tok = self.expect("WHILE", "'while'")
        self.expect("LPAREN", "'('")
        cond = self.expr()
        self.expect("RPAREN", "')'")
        body = self.stmt()
        return While(cond, body, _span_of(tok))

    def for_stmt(self) -> For:
        tok = self.expect("FOR", "'for'")
        self.expect("LPAREN", "'('")
        init: List[Stmt] = []
        if self.peek().kind != "SEMI":
            if self.peek().kind in {"INT_T", "DOUBLE_T", "BOOLEAN_T", "STRING_T"}:
                # una sola var-decl (sin ';' aquí)
                init_decl = self.var_decl_no_semi()
                init.append(init_decl)
            else:
                e = self.expr()
                init.append(ExprStmt(e, e.span))
        self.expect("SEMI", "';'")

        cond = None
        if self.peek().kind != "SEMI":
            cond = self.expr()
        self.expect("SEMI", "';'")

        step: List[Expr] = []
        if self.peek().kind != "RPAREN":
            step.append(self.expr())
            while self.match("COMMA"):
                step.append(self.expr())
        self.expect("RPAREN", "')'")
        body = self.stmt()
        return For(tuple(init), cond, tuple(step), body, _span_of(tok))

    def var_decl_no_semi(self) -> VarDecl:
        t = self.type_ref()
        name_tok = self.expect("IDENT", "nombre de variable")
        init = None
        if self.match("EQ"):
            init = self.expr()
        return VarDecl(t, name_tok.lexeme, init, _span_of(name_tok))

    def return_stmt(self) -> Return:
        tok = self.expect("RETURN", "'return'")
        expr = None
        if self.peek().kind != "SEMI":
            expr = self.expr()
        self.expect("SEMI", "';'")
        return Return(expr, _span_of(tok))

    # ---------- Expresiones ----------
    def expr(self) -> Expr:
        return self.assign()

    def assign(self) -> Expr:
        left = self.or_expr()
        if self.match("EQ"):
            val = self.assign()
            return Assign(left, val, left.span)
        return left

    def or_expr(self) -> Expr:
        e = self.and_expr()
        while self.match("OROR"):
            op_tok = self.tokens[self.i - 1]
            right = self.and_expr()
            e = Binary("||", e, right, _span_of(op_tok))
        return e

    def and_expr(self) -> Expr:
        e = self.equality()
        while self.match("ANDAND"):
            op_tok = self.tokens[self.i - 1]
            right = self.equality()
            e = Binary("&&", e, right, _span_of(op_tok))
        return e

    def equality(self) -> Expr:
        e = self.rel()
        while self.peek().kind in {"EQEQ", "NEQ"}:
            op_tok = self.peek(); self.i += 1
            right = self.rel()
            e = Binary(op_tok.lexeme, e, right, _span_of(op_tok))
        return e

    def rel(self) -> Expr:
        e = self.add()
        while self.peek().kind in {"LT", "LE", "GT", "GE"}:
            op_tok = self.peek(); self.i += 1
            right = self.add()
            e = Binary(op_tok.lexeme, e, right, _span_of(op_tok))
        return e

    def add(self) -> Expr:
        e = self.mul()
        while self.peek().kind in {"PLUS", "MINUS"}:
            op_tok = self.peek(); self.i += 1
            right = self.mul()
            e = Binary(op_tok.lexeme, e, right, _span_of(op_tok))
        return e

    def mul(self) -> Expr:
        e = self.unary()
        while self.peek().kind in {"STAR", "SLASH", "PERCENT"}:
            op_tok = self.peek(); self.i += 1
            right = self.unary()
            e = Binary(op_tok.lexeme, e, right, _span_of(op_tok))
        return e

    def unary(self) -> Expr:
        if self.peek().kind in {"BANG", "MINUS"}:
            op_tok = self.peek(); self.i += 1
            right = self.unary()
            return Unary(op_tok.lexeme, right, _span_of(op_tok))
        return self.postfix()

    def postfix(self) -> Expr:
        e = self.primary()
        while True:
            if self.match("DOT"):
                name_tok = self.expect("IDENT", "identificador después de '.'")
                e = Select(e, name_tok.lexeme, _span_of(name_tok))
                continue
            if self.match("LPAREN"):
                args: List[Expr] = []
                if self.peek().kind != "RPAREN":
                    args.append(self.expr())
                    while self.match("COMMA"):
                        args.append(self.expr())
                rparen = self.expect("RPAREN", "')'")
                e = Call(e, tuple(args), Span(e.span.line, e.span.col, rparen.end_line, rparen.end_col))
                continue
            break
        return e

    def primary(self) -> Expr:
        tok = self.peek()
        if tok.kind == "INT":
            self.i += 1
            return Literal(int(tok.lexeme), TypeRef("int"), _span_of(tok))
        if tok.kind == "DOUBLE":
            self.i += 1
            return Literal(float(tok.lexeme), TypeRef("double"), _span_of(tok))
        if tok.kind == "TRUE":
            self.i += 1
            return Literal(True, TypeRef("boolean"), _span_of(tok))
        if tok.kind == "FALSE":
            self.i += 1
            return Literal(False, TypeRef("boolean"), _span_of(tok))
        if tok.kind == "STRING":
            self.i += 1
            return Literal(tok.lexeme, TypeRef("String"), _span_of(tok))
        if tok.kind == "IDENT":
            self.i += 1
            return Ident(tok.lexeme, _span_of(tok))
        if tok.kind == "LPAREN":
            self.expect("LPAREN", "'('")
            inner = self.expr()
            self.expect("RPAREN", "')'")
            return inner

        self.i += 1
        self.diags.append(Diagnostic("error", "parser", "Expresión inválida",
                                     tok.line, tok.col, tok.end_line, tok.end_col, "PAR003"))
        return Literal(0, TypeRef("int"), _span_of(tok))

# ---------- API pública ----------
def parse(tokens: List[Token]) -> Tuple[CompilationUnit, List[Diagnostic]]:
    return Parser(tokens).parse()
