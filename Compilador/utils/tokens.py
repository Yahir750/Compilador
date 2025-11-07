from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

TokenKind = Literal[
    # Palabras clave
    "CLASS","STATIC","VOID","INT_T","DOUBLE_T","BOOLEAN_T","STRING_T",
    "IF","ELSE","WHILE","FOR","TRUE","FALSE",
    # Identificadores & literales
    "IDENT","INT","DOUBLE","STRING",
    # Operadores
    "PLUS","MINUS","STAR","SLASH","PERCENT",
    "EQEQ","NEQ","LT","LE","GT","GE",
    "ANDAND","OROR","BANG","EQ",
    # Separadores
    "SEMI","COMMA","DOT","LPAREN","RPAREN","LBRACE","RBRACE","LBRACK","RBRACK",
    # EOF
    "EOF"
]

@dataclass(frozen=True)
class Token:
    kind: TokenKind
    lexeme: str
    line: int
    col: int
    end_line: int
    end_col: int

    def __repr__(self) -> str:
        return f"Token({self.kind}, {self.lexeme!r}, {self.line}:{self.col}-{self.end_line}:{self.end_col})"
