from compiler.lexer import lex
from compiler.parser import parse
from compiler.codegen_java import emit

def test_codegen_basic_ast():
    src = """
    class Main {
        static void main() {
            int a = 1;
            if (a < 10) a = a + 1;
            while (a < 20) { a = a + 2; }
            for (a = 0; a < 5; a = a + 1) { a = a + 1; }
        }
    }
    """
    toks, _ = lex(src)
    ast, diags_p = parse(toks)
    java_out, diags_cg = emit(ast, from_stage="ast")
    assert not any(d.severity == "error" for d in diags_p)
    assert "class Main" in java_out
    assert "static void main()" in java_out
    assert "if (" in java_out and "while (" in java_out and "for (" in java_out
