public class EjemploCompleto {
    public static int fibonacci(int n) {
        if(n <= 1) {
            {
                return n;
            }
        }
        return fibonacci(n - 1)+ fibonacci(n - 2);
    }
    public static int buscar(int[] arr,int size,int valor) {
        for(int i = 0;
        i < size;
        i = i + 1) {
            {
                if((arr[i])== valor) {
                    {
                        return i;
                    }
                }
            }
        }
        return - 1;
    }
    public static void ordenar(int[] arr,int size) {
        for(int i = 0;
        i < size;
        i = i + 1) {
            {
                for(int j = 0;
                j <(size - 1);
                j = j + 1) {
                    {
                        if((arr[j])>(arr[j + 1])) {
                            {
                                int temp = arr[j];
                                arr[j] = arr[j + 1];
                                arr[j + 1] = temp;
                            }
                        }
                    }
                }
            }
        }
    }
    public static int contarPares(int[] arr,int size) {
        int count = 0;
        for(int i = 0;
        i < size;
        i = i + 1) {
            {
                int residuo =(arr[i])-(((arr[i])/ 2)* 2);
                if(residuo == 0) {
                    {
                        count = count + 1;
                    }
                }
            }
        }
        return count;
    }
    public static void imprimirArray(int[] arr,int size) {
        for(int i = 0;
        i < size;
        i = i + 1) {
            {
                System.out.println(arr[i]);
            }
        }
    }
    public static void main(String[] args) {
        System.out.println(fibonacci(7));
        int[] numeros = new int[] {
            5,2,8,1,9}
            ;
            int pos = buscar(numeros,5,8);
            System.out.println(pos);
            int pares = contarPares(numeros,5);
            System.out.println(pares);
            ordenar(numeros,5);
            imprimirArray(numeros,5);
            int nuevaPos = buscar(numeros,5,8);
            System.out.println(nuevaPos);
        }
    }
