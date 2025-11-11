public class EjemploMetodos {
    public static int sumar(int a,int b) {
        return a + b;
    }
    public static int multiplicar(int x,int y) {
        int resultado = x * y;
        return resultado;
    }
    public static double dividir(double a,double b) {
        return a / b;
    }
    public static int factorial(int n) {
        if(n <= 1) {
            {
                return 1;
            }
        }
        return n * factorial(n - 1);
    }
    public static void saludar() {
        System.out.println("Hola desde traductores de lenguaje y a corona!");
    }
    public static void main(String[] args) {
        int suma = sumar(10,20);
        System.out.println(suma);
        int producto = multiplicar(5,6);
        System.out.println(producto);
        double division = dividir(10.0,2.0);
        System.out.println(division);
        int fact = factorial(5);
        System.out.println(fact);
        saludar();
        int complejo = sumar(multiplicar(2,3),factorial(3));
        System.out.println(complejo);
    }
}
