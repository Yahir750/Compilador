from compiler.lexer import lex
from compiler.parser import parse
from compiler.ir import lower, BINOP, MOVE, IRProgram
from compiler.optimizer import optimize

def flatten_instrs(ir: IRProgram):
    return [ins for fn in ir.funcs for bb in fn.blocks for ins in bb.instrs]

def test_algebra_and_move_elim():
    src = """
    class Main {
        static void main() {
            int a = 1;
            a = a + 0;     // x+0 -> x
            a = a * 1;     // x*1 -> x
            a = a * 0;     // x*0 -> 0
            a = 0 / a;     // 0/x -> 0 (conservador si x != 0 desconocido: permitido)
            a = a - 0;     // x-0 -> x
            a = a / 1;     // x/1 -> x
        }
    }
    """
    toks, _ = lex(src)
    ast, _ = parse(toks)
    ir, _ = lower(ast)
    ir2, _ = optimize(ir, level=1)

    instrs = flatten_instrs(ir2)
    # después de optimizar, no debería haber BINOP con +0, *1, /1, -0, *0 (deberían ser MOVEs)
    assert all(not (isinstance(i, BINOP) and i.op in {"ADD","MUL","DIV","SUB"} and ("#0" in (i.a, i.b) or "#1" in (i.a, i.b))) for i in instrs)

def test_const_folding_and_cjump_const():
    src = """
    class Main {
        static void main() {
            int x = 2 + 3 * 4; // 14
            if (1 < 0) { x = 0; } else { x = x; }
        }
    }
    """
    toks, _ = lex(src)
    ast, _ = parse(toks)
    ir, _ = lower(ast)
    ir2, _ = optimize(ir, level=1)

    instrs = flatten_instrs(ir2)
    # Debe existir MOVE con #14 (const folding)
    assert any(isinstance(i, MOVE) and i.src in {"#14", "#14.0"} for i in instrs)
    # El if (false) debe transformarse a un JUMP directo a la rama false o true
    assert any(i.__class__.__name__ == "JUMP" for i in instrs)
