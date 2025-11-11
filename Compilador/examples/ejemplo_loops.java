// Ejemplo 3: Bucles (while, for) con break y continue
class EjemploLoops {
    public static void main(String[] args) {
        // While loop
        int contador = 0;
        while (contador < 5) {
            System.out.println(contador);
            contador = contador + 1;
        }
        
        // For loop
        for (int i = 0; i < 3; i = i + 1) {
            System.out.println(i);
        }
        
        // For con break
        for (int i = 0; i < 10; i = i + 1) {
            if (i == 5) {
                break;
            }
            System.out.println(i);
        }
        
        // For con continue (solo números pares)
        for (int i = 0; i < 6; i = i + 1) {
            if (i == 1 || i == 3 || i == 5) {
                continue;
            }
            System.out.println(i);
        }
    }
}
