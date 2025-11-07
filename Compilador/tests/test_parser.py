from compiler.lexer import lex
from compiler.parser import parse
from compiler.ast_nodes import *

def test_parser_simple_class():
    src = """
    class Main {
        static void main() {
            int a = 1;
            if (a < 10) a = a + 1;
        }
    }
    """
    tokens, _ = lex(src)
    ast, diags = parse(tokens)
    assert not any(d.severity == "error" for d in diags)
    assert isinstance(ast.class_decl, ClassDecl)
    assert ast.class_decl.name == "Main"
    assert len(ast.class_decl.methods) == 1
    m = ast.class_decl.methods[0]
    assert m.name == "main"
    assert isinstance(m.body, Block)
