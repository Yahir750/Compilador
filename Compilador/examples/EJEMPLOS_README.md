# 📚 Ejemplos de Código para el Compilador Java→Java

## 🎯 Características Soportadas

El compilador soporta las siguientes características de Java:

### ✅ Tipos de Datos
- `int` - Enteros
- `double` - Números de punto flotante
- `boolean` - Valores true/false
- `int[]`, `double[]` - Arrays unidimensionales

### ✅ Variables
- Declaración e inicialización
- Asignación
- Conversión implícita int→double

### ✅ Operadores
**Aritméticos**: `+`, `-`, `*`, `/`, `%` (módulo simulado)
**Comparación**: `==`, `!=`, `<`, `>`, `<=`, `>=`
**Lógicos**: `&&`, `||`, `!`

### ✅ Estructuras de Control
- `if` / `if-else`
- `while` loops
- `for` loops
- `break` - Salir del loop
- `continue` - Siguiente iteración

### ✅ Métodos
- Métodos estáticos con parámetros
- Tipos de retorno: `void`, `int`, `double`, `boolean`
- Recursión
- Sobrecarga básica

### ✅ Arrays
- Creación: `new int[size]`
- Inicialización: `new int[]{1,2,3}`
- Acceso: `arr[index]`
- Modificación: `arr[index] = value`
- Arrays como parámetros

### ✅ Salida
- `System.out.println()` para int, double, boolean

---

## 📂 Ejemplos Incluidos

### 1. **ejemplo_basico.java**
Conceptos básicos: variables, operaciones aritméticas, System.out.println
```bash
python main.py examples/ejemplo_basico.java -o output/Basico.java
```

### 2. **ejemplo_condicionales.java**
Condicionales if/else, operadores lógicos y de comparación
```bash
python main.py examples/ejemplo_condicionales.java -o output/Condicionales.java
```

### 3. **ejemplo_loops.java**
Bucles while y for, break y continue
```bash
python main.py examples/ejemplo_loops.java -o output/Loops.java
```

### 4. **ejemplo_metodos.java**
Métodos con parámetros, return, recursión (factorial)
```bash
python main.py examples/ejemplo_metodos.java -o output/Metodos.java
```

### 5. **ejemplo_arrays.java**
Arrays: creación, acceso, modificación, inicializadores
```bash
python main.py examples/ejemplo_arrays.java -o output/Arrays.java
```

### 6. **ejemplo_completo.java**
Programa completo: Fibonacci, búsqueda, ordenamiento
```bash
python main.py examples/ejemplo_completo.java -o output/Completo.java
```

### 7. **ejemplo_matematicas.java**
Algoritmos matemáticos: potencia, MCD, primos, suma de dígitos
```bash
python main.py examples/ejemplo_matematicas.java -o output/Matematicas.java
```

---

## 🚀 Cómo Probar los Ejemplos

### Opción 1: Línea de Comandos
```powershell
# Compilar
python main.py examples/ejemplo_basico.java -o output/Basico.java

# Compilar y ejecutar
cd output
javac Basico.java
java Basico
```

### Opción 2: GUI
```powershell
python main.py --gui
```
1. Click en "📂 Abrir"
2. Selecciona un ejemplo de la carpeta `examples/`
3. Click en "🔨 Compilar"
4. Click en "▶ Ejecutar"

### Opción 3: Con Optimizaciones
```powershell
# Optimización O1
python main.py examples/ejemplo_matematicas.java --O1 -o output/Matematicas.java
```

---

## 📊 Resultados Esperados

### ejemplo_basico.java
```
35
43.75
true
```

### ejemplo_condicionales.java
```
Es mayor de edad
No es niño
Puede conducir
false
true
true
```

### ejemplo_loops.java
```
0 1 2 3 4
0 1 2
0 1 2 3 4
0 2 4
```

### ejemplo_metodos.java
```
30
30
5.0
120
Hola desde un método!
12
```

### ejemplo_arrays.java
```
150
50
300
28
```

### ejemplo_completo.java
```
13
2
2
1
2
5
8
9
3
```

### ejemplo_matematicas.java
```
256
81
6
true
false
15
```

---

## ⚠️ Limitaciones Conocidas

### ❌ NO Soportado
- Clases múltiples
- Métodos no estáticos
- Strings como tipo de dato (solo en println)
- Arrays multidimensionales
- Operador `%` (módulo) - usar división y resta
- Switch/case
- do-while
- Imports
- Excepciones

### ⚡ Workarounds

**Módulo (%):**
```java
// NO: int residuo = 10 % 3;
// SÍ:
int residuo = 10 - ((10 / 3) * 3);
```

**Incremento (++):**
```java
// NO: i++;
// SÍ: i = i + 1;
```

**Operador +=:**
```java
// NO: sum += 5;
// SÍ: sum = sum + 5;
```

---

## 🎨 Probando en la GUI

La GUI incluye:
- ✨ **Syntax Highlighting** automático
- 📊 **Números de línea**
- ⚠️ **Panel de diagnósticos** con tabs (Errores/Warnings)
- 📈 **Barra de estado** con estadísticas
- 🌙 **Modo oscuro**
- 📝 **Vistas de AST e IR** para debugging

---

## 💡 Tips para Crear tus Propios Programas

1. **Empieza simple**: Prueba primero variables y operaciones básicas
2. **Agrega complejidad gradualmente**: if → loops → métodos → arrays
3. **Usa el modo AST/IR**: Para entender cómo se procesa tu código
4. **Revisa los diagnósticos**: Los mensajes de error son muy descriptivos
5. **Optimiza con O1**: Compara el código generado con y sin optimización

---

## 🔧 Debugging

Si encuentras errores:

1. **Revisa el panel de diagnósticos**: Click en el error para ir a la línea
2. **Usa la vista AST**: Verifica que el parser entendió correctamente
3. **Usa la vista IR**: Verifica la representación intermedia
4. **Compila sin optimización**: Prueba con O0 primero
5. **Simplifica el código**: Comenta partes hasta encontrar el problema

---

¡Feliz compilación! 🚀
