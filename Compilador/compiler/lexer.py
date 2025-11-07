from __future__ import annotations
from typing import List, Tuple, Dict
from compiler.diagnostics import Diagnostic
from utils.tokens import Token, TokenKind

KEYWORDS: Dict[str, TokenKind] = {
    "class": "CLASS",
    "public": "PUBLIC",        # ✅ <-- AÑADE ESTA LÍNEA
    "static": "STATIC",
    "void": "VOID",
    "int": "INT_T",
    "double": "DOUBLE_T",
    "boolean": "BOOLEAN_T",
    "String": "STRING_T",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "true": "TRUE",
    "false": "FALSE",
}


SINGLE_CHAR_TOKENS = {
    ';': "SEMI", ',': "COMMA", '.': "DOT",
    '(': "LPAREN", ')': "RPAREN", '{': "LBRACE", '}': "RBRACE",
    '[': "LBRACK", ']': "RBRACK",
    '+': "PLUS", '-': "MINUS", '*': "STAR", '/': "SLASH", '%': "PERCENT",
    '!': "BANG", '=': "EQ", '<': "LT", '>': "GT",
}

def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch in {'_', '$'}

def _is_ident_part(ch: str) -> bool:
    return ch.isalnum() or ch in {'_', '$'}

def lex(src: str) -> Tuple[List[Token], List[Diagnostic]]:
    tokens: List[Token] = []
    diags: List[Diagnostic] = []

    i = 0
    line = 1
    col = 1
    n = len(src)

    def peek(off: int = 0) -> str:
        j = i + off
        return src[j] if j < n else '\0'

    def advance() -> str:
        nonlocal i, line, col
        ch = src[i] if i < n else '\0'
        i += 1
        if ch == '\n':
            line += 1
            col = 1
        else:
            col += 1
        return ch

    def emit(kind: TokenKind, start_line: int, start_col: int, end_line: int, end_col: int, text: str) -> None:
        tokens.append(Token(kind, text, start_line, start_col, end_line, end_col))

    while i < n:
        ch = peek()

        # Espacios en blanco
        if ch.isspace():
            advance()
            continue

        # Comentarios
        if ch == '/':
            if peek(1) == '/':  # comentario de línea
                while i < n and advance() != '\n':
                    pass
                continue
            if peek(1) == '*':  # comentario de bloque
                start_line, start_col = line, col
                advance(); advance()
                while True:
                    if i >= n:
                        diags.append(Diagnostic("error","lexer","Comentario de bloque no cerrado",
                                                start_line,start_col,line,col,"LEX003"))
                        break
                    c = advance()
                    if c == '*' and peek() == '/':
                        advance()
                        break
                continue

        start_line, start_col = line, col

        # Identificadores / palabras clave
        if _is_ident_start(ch):
            text = [advance()]
            while _is_ident_part(peek()):
                text.append(advance())
            word = ''.join(text)
            kind = KEYWORDS.get(word, "IDENT")
            emit(kind, start_line, start_col, line, col-1, word)
            continue

        # Números
        if ch.isdigit():
            text = [advance()]
            while peek().isdigit():
                text.append(advance())
            has_dot = False
            if peek() == '.' and (i+1) < n and src[i+1].isdigit():
                has_dot = True
                text.append(advance())
                while peek().isdigit():
                    text.append(advance())
            num = ''.join(text)
            emit("DOUBLE" if has_dot else "INT", start_line, start_col, line, col-1, num)
            continue

        # Literales de cadena
        if ch == '"':
            advance()
            sline, scol = start_line, start_col
            out = []
            escaped = False
            terminated = False
            while i < n:
                c = advance()
                if c == '\0':
                    break
                if escaped:
                    out.append(c)
                    escaped = False
                    continue
                if c == '\\':
                    escaped = True
                    continue
                if c == '"':
                    lit = '"' + ''.join(out) + '"'
                    emit("STRING", sline, scol, line, col-1, lit)
                    terminated = True
                    break
                if c == '\n':
                    diags.append(Diagnostic("error","lexer","Cadena no cerrada antes del fin de línea",
                                            sline,scol,line,col,"LEX002"))
                    terminated = True
                    break
                out.append(c)
            if not terminated and i >= n:
                diags.append(Diagnostic("error","lexer","Cadena no cerrada al fin de archivo",
                                        sline,scol,line,col,"LEX002"))
            continue

        # Operadores de dos caracteres
        two = ch + peek(1)
        if two in ("==","!=", "<=", ">=", "&&", "||"):
            advance(); advance()
            mapping = {"==":"EQEQ","!=":"NEQ","<=":"LE",">=":"GE","&&":"ANDAND","||":"OROR"}
            emit(mapping[two], start_line, start_col, line, col-1, two)
            continue

        # Operadores / separadores de un carácter
        if ch in SINGLE_CHAR_TOKENS:
            advance()
            emit(SINGLE_CHAR_TOKENS[ch], start_line, start_col, line, col-1, ch)
            continue

        # Carácter desconocido
        bad = advance()
        diags.append(Diagnostic("error","lexer",f"Carácter inesperado: {bad!r}",
                                start_line,start_col,line,col-1,"LEX001"))

    tokens.append(Token("EOF","", line, col, line, col))
    return tokens, diags
