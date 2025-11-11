// Ejemplo 4: Métodos con parámetros y return
class EjemploMetodos {
    // Método que suma dos números
    public static int sumar(int a, int b) {
        return a + b;
    }
    
    // Método que multiplica
    public static int multiplicar(int x, int y) {
        int resultado = x * y;
        return resultado;
    }
    
    // Método con double
    public static double dividir(double a, double b) {
        return a / b;
    }
    
    // Método recursivo - factorial
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    // Método void (sin retorno)
    public static void saludar() {
        System.out.println("Hola desde un método!");
    }
    
    public static void main(String[] args) {
        // Llamadas a métodos
        int suma = sumar(10, 20);
        System.out.println(suma);
        
        int producto = multiplicar(5, 6);
        System.out.println(producto);
        
        double division = dividir(10.0, 2.0);
        System.out.println(division);
        
        int fact = factorial(5);
        System.out.println(fact);
        
        saludar();
        
        // Llamadas anidadas
        int complejo = sumar(multiplicar(2, 3), factorial(3));
        System.out.println(complejo);
    }
}
