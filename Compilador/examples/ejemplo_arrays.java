// Ejemplo 5: Arrays - declaración, acceso, modificación
class EjemploArrays {
    // Método que suma elementos de un array
    public static int sumaArray(int[] arr, int size) {
        int total = 0;
        for (int i = 0; i < size; i = i + 1) {
            total = total + arr[i];
        }
        return total;
    }
    
    // Método que encuentra el máximo
    public static int maximo(int[] arr, int size) {
        int max = arr[0];
        for (int i = 1; i < size; i = i + 1) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }
    
    // Método que duplica valores
    public static void duplicar(int[] arr, int size) {
        for (int i = 0; i < size; i = i + 1) {
            arr[i] = arr[i] * 2;
        }
    }
    
    public static void main(String[] args) {
        // Crear array con new
        int[] numeros = new int[5];
        numeros[0] = 10;
        numeros[1] = 20;
        numeros[2] = 30;
        numeros[3] = 40;
        numeros[4] = 50;
        
        // Sumar elementos
        int suma = sumaArray(numeros, 5);
        System.out.println(suma);
        
        // Encontrar máximo
        int max = maximo(numeros, 5);
        System.out.println(max);
        
        // Duplicar valores (modifica el array)
        duplicar(numeros, 5);
        int nuevaSuma = sumaArray(numeros, 5);
        System.out.println(nuevaSuma);
        
        // Array con inicializador
        int[] primos = new int[]{2, 3, 5, 7, 11};
        int sumaPrimos = sumaArray(primos, 5);
        System.out.println(sumaPrimos);
    }
}
