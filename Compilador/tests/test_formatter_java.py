from compiler.formatter_java import format_java

def test_formatter_basic_braces_and_indents():
    src = """
    class Main{static void main(){int a=1;if(a<10){a=a+1;}else{a=a+2;}while(a<20){a=a+3;}}}
    """
    out, diags = format_java(src)
    # Llaves y sangrías bien colocadas
    assert "class Main {" in out
    assert "if (a < 10)" in out
    assert "else" in out
    assert "while (a < 20)" in out
    assert "\n    static void main()" in out
    # No debe haber errores
    assert all(d.severity != "error" for d in diags)
