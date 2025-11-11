public class TestArrays {
    // Función que suma elementos de un array
    public static int sumArray(int[] arr) {
        int sum = 0;
        int i = 0;
        while (i < 5) {
            sum = sum + arr[i];
            i = i + 1;
        }
        return sum;
    }
    
    // Función que encuentra el máximo
    public static int maxArray(int[] arr) {
        int max = arr[0];
        for (int i = 1; i < 5; i = i + 1) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }
    
    // Función que modifica el array
    public static void doubleValues(int[] arr) {
        for (int i = 0; i < 5; i = i + 1) {
            arr[i] = arr[i] * 2;
        }
    }
    
    public static void main(String[] args) {
        // Crear array con new
        int[] numbers = new int[5];
        
        // Asignar valores
        numbers[0] = 10;
        numbers[1] = 20;
        numbers[2] = 30;
        numbers[3] = 40;
        numbers[4] = 50;
        
        // Suma
        int total = sumArray(numbers);
        System.out.println(total);  // 150
        
        // Máximo
        int maximum = maxArray(numbers);
        System.out.println(maximum);  // 50
        
        // Modificar array
        doubleValues(numbers);
        int newTotal = sumArray(numbers);
        System.out.println(newTotal);  // 300
        
        // Array con inicializador
        int[] primes = new int[]{2, 3, 5, 7, 11};
        int primeSum = sumArray(primes);
        System.out.println(primeSum);  // 28
    }
}
