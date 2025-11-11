// Ejemplo 6: Programa completo que usa TODAS las características
class EjemploCompleto {
    // Fibonacci recursivo
    public static int fibonacci(int n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    // Búsqueda en array
    public static int buscar(int[] arr, int size, int valor) {
        for (int i = 0; i < size; i = i + 1) {
            if (arr[i] == valor) {
                return i;
            }
        }
        return -1;
    }
    
    // Ordenamiento burbuja simple
    public static void ordenar(int[] arr, int size) {
        for (int i = 0; i < size; i = i + 1) {
            for (int j = 0; j < size - 1; j = j + 1) {
                if (arr[j] > arr[j + 1]) {
                    // Intercambiar
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }
    
    // Contar números pares
    public static int contarPares(int[] arr, int size) {
        int count = 0;
        for (int i = 0; i < size; i = i + 1) {
            int residuo = arr[i] - ((arr[i] / 2) * 2);
            if (residuo == 0) {
                count = count + 1;
            }
        }
        return count;
    }
    
    // Imprimir array
    public static void imprimirArray(int[] arr, int size) {
        for (int i = 0; i < size; i = i + 1) {
            System.out.println(arr[i]);
        }
    }
    
    public static void main(String[] args) {
        // Fibonacci
        System.out.println(fibonacci(7));
        
        // Array desordenado
        int[] numeros = new int[]{5, 2, 8, 1, 9};
        
        // Buscar antes de ordenar
        int pos = buscar(numeros, 5, 8);
        System.out.println(pos);
        
        // Contar pares
        int pares = contarPares(numeros, 5);
        System.out.println(pares);
        
        // Ordenar
        ordenar(numeros, 5);
        
        // Imprimir ordenado
        imprimirArray(numeros, 5);
        
        // Buscar después de ordenar
        int nuevaPos = buscar(numeros, 5, 8);
        System.out.println(nuevaPos);
    }
}
