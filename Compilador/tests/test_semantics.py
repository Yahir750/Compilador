from compiler.lexer import lex
from compiler.parser import parse
from compiler.semantics import analyze

def _has_error(diags, code):
    return any(d.severity=="error" and d.code==code for d in diags)

def _has_warning(diags, code):
    return any(d.severity=="warning" and d.code==code for d in diags)

def test_use_before_declare_and_shadow():
    src = """
    class Main {
        static void main() {
            int x = y;      // uso antes de declarar
            int y = 1;
            {
                int y = 2; // sombra
                y = y + 1;
            }
            if (x < 10 && true) {
                System.out.println(x);
            }
        }
    }
    """
    toks, d1 = lex(src)
    ast, d2 = parse(toks)
    ast2, d3, sym = analyze(ast)
    diags = [*d1, *d2, *d3]
    assert _has_error(diags, "SEM_UNDECL")
    assert _has_warning(diags, "SEM_SHADOW")

def test_type_checks_and_println_arity():
    src = """
    class Main {
        static void main() {
            int a = 1;
            double b = a + 2.5;
            boolean c = (a < b);
            if (c) {
                System.out.println(b);
                System.out.println(); // error de aridad
            }
            a = c; // error de asignación
        }
    }
    """
    toks, _ = lex(src)
    ast, diags_p = parse(toks)
    _, diags_s, _ = analyze(ast)
    # println sin args -> error
    assert any(d.code == "SEM_ARGC" for d in diags_s)
    # asignación boolean -> int -> error
    assert any(d.code == "SEM_ASSIGN" and d.severity == "error" for d in diags_s)

def test_unused_variable_warning():
    src = """
    class Main {
        static void main() {
            int a = 0; // no usado
            int b = 1;
            b = b + 1;
        }
    }
    """
    toks, _ = lex(src)
    ast, _ = parse(toks)
    _, diags_s, _ = analyze(ast)
    assert any(d.code == "SEM_UNUSED" and d.severity == "warning" for d in diags_s)
