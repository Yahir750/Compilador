# COMPILADOR JAVA → JAVA
## Manual de Usuario

---

## CONTENIDO

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Guía de Inicio Rápido](#guía-de-inicio-rápido)
5. [Uso desde Línea de Comandos](#uso-desde-línea-de-comandos)
6. [Uso de la Interfaz Gráfica](#uso-de-la-interfaz-gráfica)
7. [Ejemplos Prácticos](#ejemplos-prácticos)
8. [Resolución de Problemas](#resolución-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 1. INTRODUCCIÓN

### ¿Qué es este compilador?

Es una herramienta que traduce código Java a código Java optimizado, validando la sintaxis y semántica del programa. Incluye análisis léxico, sintáctico, semántico, optimización y formateo de código.

### ¿Para qué sirve?

- **Validar** código Java antes de compilarlo
- **Optimizar** código Java automáticamente
- **Formatear** código para mejor legibilidad
- **Aprender** sobre compiladores y sus fases
- **Diagnosticar** errores con mensajes claros

---

## 2. REQUISITOS DEL SISTEMA

### Software Necesario

**Obligatorios:**
- Python 3.8 o superior
- JDK (Java Development Kit) 8 o superior

**Opcionales:**
- Git (para clonar el repositorio)

### Sistemas Operativos Soportados

- Windows 10/11
- Linux (Ubuntu, Debian, Fedora, etc.)
- macOS 10.14 o superior

### Recursos de Hardware

- Procesador: 1 GHz o superior
- RAM: 512 MB mínimo (1 GB recomendado)
- Espacio en disco: 50 MB

---

## 3. INSTALACIÓN

### Paso 1: Instalar Python

**Windows:**
1. Descargar de https://www.python.org/downloads/
2. Ejecutar instalador
3. ✓ Marcar "Add Python to PATH"
4. Completar instalación

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

### Paso 2: Instalar JDK

**Windows:**
1. Descargar de https://www.oracle.com/java/technologies/downloads/
2. Ejecutar instalador
3. Configurar variable de entorno JAVA_HOME

**Linux:**
```bash
sudo apt install default-jdk
```

**macOS:**
```bash
brew install openjdk
```

### Paso 3: Verificar Instalación

Abrir terminal y ejecutar:

```bash
python --version
# Debe mostrar: Python 3.x.x

java -version
# Debe mostrar: java version "1.8.x" o superior

javac -version
# Debe mostrar: javac 1.8.x o superior
```

### Paso 4: Obtener el Compilador

**Opción 1: Clonar repositorio**
```bash
git clone https://github.com/Yahir750/Compilador.git
cd Compilador
```

**Opción 2: Descargar ZIP**
1. Descargar archivo ZIP
2. Extraer a una carpeta
3. Abrir terminal en esa carpeta

### Paso 5: Verificar Estructura

Asegúrate de tener:
```
Compilador/
├── compiler/
├── utils/
├── gui/
├── examples/
├── main.py
└── pyproject.toml
```

---

## 4. GUÍA DE INICIO RÁPIDO

### Opción 1: Usar la Interfaz Gráfica (Recomendado)

1. Abrir terminal en la carpeta del compilador
2. Ejecutar:
   ```bash
   python main.py --gui
   ```
3. Se abrirá la ventana del compilador
4. Escribir o abrir código Java
5. Click en "Compilar"
6. Click en "Ejecutar" para ver resultados

### Opción 2: Línea de Comandos

1. Crear archivo `Hola.java`:
   ```java
   class Hola {
       public static void main(String[] args) {
           System.out.println("Hola Mundo!");
       }
   }
   ```

2. Compilar:
   ```bash
   python main.py Hola.java -o HolaCompilado.java
   ```

3. Ejecutar:
   ```bash
   javac HolaCompilado.java
   java Hola
   ```

---

## 5. USO DESDE LÍNEA DE COMANDOS

### Sintaxis Básica

```bash
python main.py [archivo_entrada] [opciones]
```

### Opciones Disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `archivo.java` | Archivo de entrada | `main.py codigo.java` |
| `-o ARCHIVO` | Archivo de salida | `-o salida.java` |
| `--O0` | Sin optimización | `--O0` |
| `--O1` | Con optimización | `--O1` |
| `--ast` | Mostrar AST en JSON | `--ast` |
| `--ir` | Mostrar IR en JSON | `--ir` |
| `--json` | Salida completa en JSON | `--json` |
| `--gui` | Abrir interfaz gráfica | `--gui` |

### Ejemplos de Uso

**1. Compilación Simple:**
```bash
python main.py examples/ejemplo_basico.java -o output/Basico.java
```

**2. Con Optimización:**
```bash
python main.py codigo.java --O1 -o codigo_optimizado.java
```

**3. Ver Estructura AST:**
```bash
python main.py codigo.java --ast
```

**4. Ver Representación Intermedia:**
```bash
python main.py codigo.java --ir
```

**5. Salida JSON Completa:**
```bash
python main.py codigo.java --json > resultado.json
```

**6. Desde Entrada Estándar:**
```bash
# Linux/Mac
cat codigo.java | python main.py

# Windows
type codigo.java | python main.py
```

### Interpretación de Resultados

**Compilación Exitosa:**
```bash
python main.py ejemplo.java -o salida.java
# Muestra el código Java generado
# Código de salida: 0
```

**Compilación con Errores:**
```bash
python main.py error.java
# Muestra JSON con errores y warnings
# Código de salida: 1
```

**Error Interno:**
```bash
# Código de salida: 2
```

---

## 6. USO DE LA INTERFAZ GRÁFICA

### Iniciar la GUI

```bash
python main.py --gui
```

### Componentes de la Interfaz

#### Barra de Herramientas Superior

**Botones de Archivo:**
- **Abrir**: Cargar archivo .java existente
- **Guardar**: Guardar salida compilada

**Botones de Compilación:**
- **Compilar**: Compilar el código actual
- **Ejecutar**: Compilar y ejecutar automáticamente

**Optimización:**
- **O0**: Sin optimizaciones
- **O1**: Con optimizaciones locales

**Vista:**
- **Java**: Mostrar código Java compilado
- **AST**: Mostrar árbol de sintaxis (debugging)
- **IR**: Mostrar representación intermedia (debugging)

**Apariencia:**
- **Modo oscuro**: Cambiar tema visual

#### Panel Izquierdo: Editor de Código

- **Números de línea**: Referencia visual
- **Syntax highlighting**: Colores para palabras clave
- **Edición libre**: Escribe o pega código

#### Panel Derecho: Salida

- Muestra el código compilado (vista Java)
- Muestra AST/IR (vistas de debugging)
- Muestra salida de ejecución

#### Panel Inferior: Diagnósticos

**3 Pestañas:**
- **Todos**: Todos los diagnósticos
- **Errores (N)**: Solo errores con contador
- **Warnings (N)**: Solo advertencias con contador

**Interacción:**
- Click en error/warning para saltar a la línea

#### Barra de Estado

- Muestra estado actual de compilación
- Muestra tiempo de compilación
- Muestra contadores de errores/warnings

### Flujo de Trabajo en GUI

**1. Crear/Abrir Código:**
- Escribir directamente en el editor, o
- Click "Abrir" y seleccionar archivo .java

**2. Compilar:**
- Click "Compilar"
- Revisar panel de salida
- Revisar diagnósticos si hay errores

**3. Corregir Errores:**
- Click en error en panel de diagnósticos
- Se resalta la línea del error
- Corregir código
- Compilar nuevamente

**4. Ejecutar:**
- Click "Ejecutar"
- Ver salida del programa en panel derecho

**5. Guardar:**
- Click "Guardar"
- Seleccionar ubicación
- Guardar archivo compilado

### Atajos de Teclado

- `Ctrl+Z`: Deshacer
- `Ctrl+Y`: Rehacer
- `Ctrl+C`: Copiar
- `Ctrl+V`: Pegar
- `Ctrl+X`: Cortar
- `Ctrl+A`: Seleccionar todo

### Preferencias

**Modo Oscuro:**
- Fondo oscuro para reducir fatiga visual
- Colores ajustados para mejor contraste
- Syntax highlighting adaptado

**Optimización:**
- O0: Código sin modificar, compilación rápida
- O1: Código optimizado, compilación ligeramente más lenta

---

## 7. EJEMPLOS PRÁCTICOS

### Ejemplo 1: Hola Mundo

**Código:**
```java
class HolaMundo {
    public static void main(String[] args) {
        System.out.println("Hola Mundo!");
    }
}
```

**Compilar:**
```bash
python main.py hola.java -o HolaMundo.java
javac HolaMundo.java
java HolaMundo
```

**Salida:**
```
Hola Mundo!
```

### Ejemplo 2: Calculadora Simple

**Código:**
```java
class Calculadora {
    public static int sumar(int a, int b) {
        return a + b;
    }
    
    public static double dividir(double a, double b) {
        return a / b;
    }
    
    public static void main(String[] args) {
        int suma = sumar(10, 5);
        System.out.println(suma);
        
        double division = dividir(10.0, 2.0);
        System.out.println(division);
    }
}
```

**Salida:**
```
15
5.0
```

### Ejemplo 3: Factorial Recursivo

**Código:**
```java
class Factorial {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static void main(String[] args) {
        System.out.println(factorial(5));
        System.out.println(factorial(10));
    }
}
```

**Salida:**
```
120
3628800
```

### Ejemplo 4: Trabajo con Arrays

**Código:**
```java
class SumaArray {
    public static int sumar(int[] arr, int size) {
        int total = 0;
        for (int i = 0; i < size; i = i + 1) {
            total = total + arr[i];
        }
        return total;
    }
    
    public static void main(String[] args) {
        int[] numeros = new int[]{10, 20, 30, 40, 50};
        int suma = sumar(numeros, 5);
        System.out.println(suma);
    }
}
```

**Salida:**
```
150
```

### Ejemplo 5: Números Primos

**Código:**
```java
class Primos {
    public static boolean esPrimo(int n) {
        if (n <= 1) {
            return false;
        }
        for (int i = 2; i < n; i = i + 1) {
            int residuo = n - ((n / i) * i);
            if (residuo == 0) {
                return false;
            }
        }
        return true;
    }
    
    public static void main(String[] args) {
        for (int i = 2; i < 20; i = i + 1) {
            if (esPrimo(i)) {
                System.out.println(i);
            }
        }
    }
}
```

**Salida:**
```
2
3
5
7
11
13
17
19
```

### Probando Ejemplos Incluidos

El compilador incluye 7 ejemplos listos para probar:

```bash
# Probar todos automáticamente
.\probar_ejemplos.ps1

# O uno por uno
python main.py examples/ejemplo_basico.java -o output/EjemploBasico.java
python main.py examples/ejemplo_metodos.java -o output/EjemploMetodos.java
python main.py examples/ejemplo_arrays.java -o output/EjemploArrays.java
```

---

## 8. RESOLUCIÓN DE PROBLEMAS

### Problema: "python no se reconoce como comando"

**Solución:**
1. Verificar que Python esté instalado
2. Agregar Python al PATH del sistema
3. Intentar con `python3` en lugar de `python`

### Problema: "javac no se reconoce como comando"

**Solución:**
1. Verificar que JDK esté instalado
2. Agregar JDK bin al PATH
3. Configurar JAVA_HOME

**Windows:**
```
JAVA_HOME = C:\Program Files\Java\jdk-xx
PATH = %JAVA_HOME%\bin
```

### Problema: "ModuleNotFoundError: No module named 'compiler'"

**Solución:**
1. Verificar que estés en la carpeta correcta
2. Verificar estructura de directorios
3. Ejecutar desde la carpeta raíz del proyecto

### Problema: Errores de sintaxis no detectados

**Solución:**
1. Revisar que el código use sintaxis soportada
2. Ver sección de limitaciones en documentación técnica
3. Usar construcciones alternativas

### Problema: La GUI no abre

**Solución:**
1. Verificar que tkinter esté instalado:
   ```bash
   python -c "import tkinter"
   ```
2. En Linux, instalar tk:
   ```bash
   sudo apt install python3-tk
   ```
3. Intentar modo CLI si GUI no funciona

### Problema: Código compila pero no ejecuta

**Solución:**
1. Verificar que el archivo .java tenga el nombre correcto de la clase
2. Asegurarse de tener método `main` con firma correcta:
   ```java
   public static void main(String[] args)
   ```
3. Revisar errores de javac

### Problema: Optimización da resultados incorrectos

**Solución:**
1. Compilar sin optimización (--O0)
2. Reportar el bug con código de ejemplo
3. Usar modo IR para depurar

---

## 9. PREGUNTAS FRECUENTES

### ¿Qué versiones de Java soporta?

El compilador genera código compatible con Java 8 y superior. El subconjunto de Java soportado está definido en la documentación técnica.

### ¿Puedo usar librerías externas?

No, actualmente solo se soporta código Java puro sin imports ni librerías externas.

### ¿Soporta programación orientada a objetos completa?

No, solo soporta métodos estáticos en una sola clase. No soporta herencia, interfaces, ni instancias de objetos.

### ¿Cómo implemento el operador módulo (%) si no está soportado?

Usa la fórmula: `residuo = a - (a/b)*b`

```java
// En lugar de: int r = 10 % 3;
int r = 10 - ((10 / 3) * 3);  // r = 1
```

### ¿Puedo usar i++ o ++i?

No, usa `i = i + 1` en su lugar.

### ¿Soporta arrays multidimensionales?

No, solo arrays unidimensionales. Para simular 2D, usa arrays con cálculo de índice manual.

### ¿La optimización puede cambiar el comportamiento del programa?

No, las optimizaciones son seguras y preservan la semántica del programa. Solo mejoran el rendimiento o reducen código redundante.

### ¿Cómo reporto un error o bug?

1. Verifica que uses sintaxis soportada
2. Crea un ejemplo mínimo que reproduzca el error
3. Incluye el código fuente y el mensaje de error
4. Reporta en el repositorio de GitHub

### ¿Puedo contribuir al proyecto?

Sí, el proyecto es de código abierto. Fork el repositorio, haz tus cambios y envía un pull request.

### ¿Hay planes para soportar más características?

Sí, futuras versiones pueden incluir:
- Strings como tipo completo
- Arrays multidimensionales
- Operador módulo nativo
- Switch/case
- Más optimizaciones

---

## APÉNDICES

### A. Sintaxis Soportada (Resumen)

**Tipos:** `int`, `double`, `boolean`, `int[]`, `double[]`

**Operadores:** `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!`

**Control:** `if`, `if-else`, `while`, `for`, `break`, `continue`, `return`

**Métodos:** `public static tipo nombre(params) { ... }`

**Arrays:** `new tipo[size]`, `new tipo[]{init}`, `arr[index]`

**I/O:** `System.out.println(expr)`

### B. Códigos de Salida

| Código | Significado |
|--------|-------------|
| 0 | Compilación exitosa |
| 1 | Errores de compilación |
| 2 | Error interno del compilador |

### C. Recursos Adicionales

**Documentación:**
- `DOCUMENTACION_TECNICA.md`: Especificaciones técnicas completas
- `examples/EJEMPLOS_README.md`: Guía de ejemplos

**Scripts:**
- `probar_ejemplos.ps1`: Prueba automática de todos los ejemplos
- `probar_ejemplos.bat`: Versión batch para Windows

**Contacto:**
- GitHub: https://github.com/Yahir750/Compilador
- Issues: https://github.com/Yahir750/Compilador/issues

---

**Versión:** 1.0
**Fecha:** Noviembre 2025
**Licencia:** MIT
