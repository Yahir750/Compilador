from compiler.lexer import lex
from utils.tokens import Token

def kinds(tokens):
    return [t.kind for t in tokens]

def lexemes(tokens):
    return [t.lexeme for t in tokens]

def test_lexer_simple_assignment():
    src = "int a=1; a=a+2;"
    toks, diags = lex(src)
    assert not any(d.severity=="error" for d in diags)
    # Secuencia esperada
    expected = ["INT_T","IDENT","EQ","INT","SEMI","IDENT","EQ","IDENT","PLUS","INT","SEMI","EOF"]
    assert kinds(toks) == expected
    assert lexemes(toks)[0] == "int"
    assert lexemes(toks)[1] == "a"
    assert lexemes(toks)[3] == "1"
