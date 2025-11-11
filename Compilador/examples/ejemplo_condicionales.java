// Ejemplo 2: Condicionales y operadores lógicos
class EjemploCondicionales {
    public static void main(String[] args) {
        int edad = 18;
        boolean tieneLicencia = true;
        
        // If simple
        if (edad >= 18) {
            System.out.println("Es mayor de edad");
        }
        
        // If-else
        if (edad < 13) {
            System.out.println("Niño");
        } else {
            System.out.println("No es niño");
        }
        
        // Operadores lógicos (&&, ||)
        if (edad >= 18 && tieneLicencia) {
            System.out.println("Puede conducir");
        }
        
        // Operadores de comparación
        boolean mayor = edad > 21;
        boolean igual = edad == 18;
        boolean diferente = edad != 25;
        
        System.out.println(mayor);
        System.out.println(igual);
        System.out.println(diferente);
    }
}
