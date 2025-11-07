from compiler.lexer import lex
from compiler.parser import parse
from compiler.ir import lower, LABEL, CJUMP, JUMP, IRProgram

def test_ir_if_while_for():
    src = """
    class Main {
        static void main() {
            int a = 0;
            if (a < 10) { a = a + 1; } else { a = a + 2; }
            while (a < 20) { a = a + 3; }
            for (a = 0; a < 5; a = a + 1) { System.out.println(a); }
        }
    }
    """
    toks, _ = lex(src)
    ast, diags_p = parse(toks)
    ir, diags_ir = lower(ast)
    assert not any(d.severity=="error" for d in diags_p), diags_p
    assert not any(d.severity=="error" for d in diags_ir), diags_ir
    assert isinstance(ir, IRProgram)
    f = ir.funcs[0]
    # Debe haber etiquetas y condicionales
    kinds = [type(instr).__name__ for b in f.blocks for instr in b.instrs]
    assert "LABEL" in kinds and "CJUMP" in kinds and "JUMP" in kinds
