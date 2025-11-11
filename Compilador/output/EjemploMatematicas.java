public class EjemploMatematicas {
    public static int potencia(int base,int exp) {
        if(exp == 0) {
            {
                return 1;
            }
        }
        int resultado = 1;
        for(int i = 0;
        i < exp;
        i = i + 1) {
            {
                resultado = resultado * base;
            }
        }
        return resultado;
    }
    public static int mcd(int a,int b) {
        while(b != 0) {
            {
                int temp = b;
                b = a -((a / b)* b);
                a = temp;
            }
        }
        return a;
    }
    public static boolean esPrimo(int n) {
        if(n <= 1) {
            {
                return false;
            }
        }
        if(n <= 3) {
            {
                return true;
            }
        }
        for(int i = 2;
        i < n;
        i = i + 1) {
            {
                if((n -((n / i)* i))== 0) {
                    {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    public static int sumaDigitos(int n) {
        int suma = 0;
        while(n > 0) {
            {
                suma = suma +(n -((n / 10)* 10));
                n = n / 10;
            }
        }
        return suma;
    }
    public static void main(String[] args) {
        System.out.println(potencia(2,8));
        System.out.println(potencia(3,4));
        System.out.println(mcd(48,18));
        System.out.println(esPrimo(17));
        System.out.println(esPrimo(18));
        System.out.println(sumaDigitos(12345));
    }
}
