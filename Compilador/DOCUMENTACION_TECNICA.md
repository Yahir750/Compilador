# COMPILADOR JAVA → JAVA
## Documentación Técnica Completa

---

## ÍNDICE

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes del Compilador](#componentes-del-compilador)
4. [Fases de Compilación](#fases-de-compilación)
5. [Características Implementadas](#características-implementadas)
6. [Especificaciones Técnicas](#especificaciones-técnicas)
7. [Manejo de Errores](#manejo-de-errores)
8. [Optimizaciones](#optimizaciones)
9. [Limitaciones y Restricciones](#limitaciones-y-restricciones)
10. [Pruebas y Validación](#pruebas-y-validación)

---

## 1. INTRODUCCIÓN

### 1.1 Descripción General

Este proyecto implementa un compilador completo que traduce código fuente Java a código Java optimizado, pasando por todas las fases tradicionales de compilación: análisis léxico, análisis sintáctico, análisis semántico, generación de representación intermedia (IR), optimización y generación de código objetivo.

### 1.2 Propósito

El compilador sirve como herramienta educativa y funcional para:
- Demostrar las fases de compilación
- Validar y optimizar código Java
- Proporcionar diagnósticos detallados de errores
- Generar código Java formateado y optimizado

### 1.3 Tecnologías Utilizadas

- **Lenguaje de implementación:** Python 3.x
- **Paradigma:** Orientado a objetos con tipos estáticos (type hints)
- **Estructuras de datos:** Dataclasses para AST e IR
- **GUI:** Tkinter/ttk
- **Validación:** javac (Java Compiler) y java (JVM)

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Arquitectura de Múltiples Pasadas

El compilador sigue una arquitectura de pipeline con las siguientes etapas:

```
Código Fuente Java
        ↓
    [LEXER] ← Análisis Léxico
        ↓
    Tokens
        ↓
    [PARSER] ← Análisis Sintáctico
        ↓
    AST (Abstract Syntax Tree)
        ↓
    [SEMANTICS] ← Análisis Semántico
        ↓
    AST Tipado + Tabla de Símbolos
        ↓
    [IR] ← Generación de Representación Intermedia
        ↓
    CFG + Three-Address Code
        ↓
    [OPTIMIZER] ← Optimización
        ↓
    IR Optimizado
        ↓
    [CODEGEN] ← Generación de Código
        ↓
    Código Java Raw
        ↓
    [FORMATTER] ← Formateo
        ↓
    Código Java Final
```

### 2.2 Estructura de Directorios

```
Compilador/
├── compiler/           # Núcleo del compilador
│   ├── lexer.py       # Análisis léxico
│   ├── parser.py      # Análisis sintáctico
│   ├── ast_nodes.py   # Definiciones del AST
│   ├── semantics.py   # Análisis semántico
│   ├── ir.py          # Representación intermedia
│   ├── optimizer.py   # Optimizador
│   ├── codegen_java.py # Generador de código
│   ├── formatter_java.py # Formateador
│   └── diagnostics.py # Sistema de diagnósticos
├── utils/             # Utilidades
│   ├── tokens.py      # Tipos de tokens
│   ├── symbols.py     # Tabla de símbolos
│   ├── config.py      # Configuración
│   └── visitors.py    # Patrones visitor
├── gui/               # Interfaz gráfica
│   ├── app.py         # Aplicación principal
│   └── components.py  # Componentes GUI
├── tests/             # Suite de pruebas
├── examples/          # Ejemplos de código
├── main.py            # Punto de entrada CLI
└── pyproject.toml     # Configuración del proyecto
```

---

## 3. COMPONENTES DEL COMPILADOR

### 3.1 Lexer (Análisis Léxico)

**Archivo:** `compiler/lexer.py`

**Función:** Convierte el texto fuente en una secuencia de tokens.

**Características:**
- Reconocimiento de palabras clave (27 keywords)
- Identificadores (variables, métodos, clases)
- Literales (enteros, decimales, booleanos)
- Operadores (aritméticos, lógicos, comparación)
- Delimitadores (paréntesis, llaves, corchetes)
- Comentarios de línea (`//`) y bloque (`/* */`)
- Manejo de espacios en blanco

**Tokens Soportados:**
```python
Palabras clave: class, public, static, void, int, double, boolean,
                if, else, while, for, return, new, true, false,
                break, continue, System.out.println

Operadores: +, -, *, /, %, ==, !=, <, >, <=, >=, &&, ||, !, =

Delimitadores: (, ), {, }, [, ], ;, ,, .
```

**Ejemplo:**
```java
int x = 10;
```
Genera tokens:
```
INT_T, IDENT("x"), ASSIGN, INT_LIT(10), SEMICOLON
```

### 3.2 Parser (Análisis Sintáctico)

**Archivo:** `compiler/parser.py`

**Función:** Construye un Árbol de Sintaxis Abstracta (AST) a partir de los tokens.

**Método:** Recursive Descent Parser con precedencia de operadores.

**Gramática Soportada:**

```bnf
programa ::= clase

clase ::= "class" ID "{" miembro* "}"

miembro ::= metodo

metodo ::= "public" "static" tipo ID "(" parametros? ")" bloque

tipo ::= "void" | "int" | "double" | "boolean" | tipo "[" "]"

parametros ::= tipo ID ("," tipo ID)*

bloque ::= "{" statement* "}"

statement ::= declaracion
            | asignacion
            | if_stmt
            | while_stmt
            | for_stmt
            | return_stmt
            | break_stmt
            | continue_stmt
            | expr_stmt

expresion ::= asignacion
            | logica_or

logica_or ::= logica_and ("||" logica_and)*

logica_and ::= igualdad ("&&" igualdad)*

igualdad ::= comparacion (("==" | "!=") comparacion)*

comparacion ::= suma (("<" | ">" | "<=" | ">=") suma)*

suma ::= multiplicacion (("+" | "-") multiplicacion)*

multiplicacion ::= unaria (("*" | "/") unaria)*

unaria ::= ("!" | "-") unaria | postfix

postfix ::= primaria ("[" expresion "]" | "(" args? ")")*

primaria ::= literal | ID | "(" expresion ")" | "new" tipo "[" expr "]"
```

**Nodos del AST:**
- `Program`: Raíz del árbol
- `ClassDecl`: Declaración de clase
- `MethodDecl`: Declaración de método
- `VarDecl`: Declaración de variable
- `IfStmt`, `WhileStmt`, `ForStmt`: Estructuras de control
- `ReturnStmt`, `BreakStmt`, `ContinueStmt`: Control de flujo
- `BinaryOp`, `UnaryOp`: Operaciones
- `MethodCall`: Llamadas a métodos
- `ArrayAccess`, `NewArray`: Operaciones con arrays

### 3.3 Semantic Analyzer (Análisis Semántico)

**Archivo:** `compiler/semantics.py`

**Función:** Valida la corrección semántica y construye la tabla de símbolos.

**Verificaciones Realizadas:**

1. **Tipos:**
   - Compatibilidad de tipos en operaciones
   - Conversión implícita int → double (widening)
   - Validación de tipos en asignaciones

2. **Símbolos:**
   - Variables declaradas antes de uso
   - No redeclaración de variables en el mismo scope
   - Resolución de nombres de métodos

3. **Control de Flujo:**
   - `return` en métodos no-void
   - `break`/`continue` solo dentro de loops
   - Tipos de retorno coinciden con declaración

4. **Arrays:**
   - Índices de tipo `int`
   - Tamaños de array son enteros positivos
   - Acceso coherente con tipo declarado

5. **Métodos:**
   - Aridad correcta en llamadas
   - Tipos de parámetros compatibles
   - Métodos declarados antes de uso

**Tabla de Símbolos:**
```python
class Symbol:
    name: str           # Nombre del símbolo
    kind: str          # Tipo (int, double, boolean, array)
    scope_level: int   # Nivel de anidamiento
    metadata: dict     # Información adicional (parámetros, etc.)
```

### 3.4 IR Generator (Representación Intermedia)

**Archivo:** `compiler/ir.py`

**Función:** Genera representación intermedia de bajo nivel.

**Formato:** Three-Address Code (TAC) + Control Flow Graph (CFG)

**Instrucciones IR:**

```python
LABEL(name)              # Etiqueta de destino
JUMP(target)             # Salto incondicional
CJUMP(cond, true, false) # Salto condicional
MOVE(dest, src)          # Asignación
BINOP(dest, left, op, right)  # Operación binaria
UNOP(dest, op, operand)  # Operación unaria
CMP(dest, left, op, right)    # Comparación
CALL(dest, func, args)   # Llamada a función
RET(value)              # Retorno
```

**Ejemplo:**
```java
int x = 5 + 3;
```
Genera IR:
```
t0 = 5 + 3
x = t0
```

**Control Flow Graph (CFG):**
- Cada bloque básico es un nodo
- Aristas representan flujo de control
- Permite análisis de alcance y viveza

### 3.5 Optimizer (Optimizador)

**Archivo:** `compiler/optimizer.py`

**Función:** Mejora el código generado.

**Niveles de Optimización:**

**O0 (Sin optimización):**
- Código tal como se genera

**O1 (Optimizaciones locales):**
- Constant folding (evaluación de constantes)
- Constant propagation (propagación de constantes)
- Dead code elimination (eliminación de código muerto)
- Algebraic simplification (simplificación algebraica)

**Transformaciones:**

1. **Constant Folding:**
```
t0 = 2 + 3  →  t0 = 5
```

2. **Constant Propagation:**
```
x = 5       →  x = 5
y = x + 2   →  y = 7
```

3. **Dead Code Elimination:**
```
t0 = 5      (eliminado si t0 nunca se usa)
```

4. **Algebraic Simplification:**
```
x * 1  →  x
x + 0  →  x
x * 0  →  0
```

### 3.6 Code Generator (Generación de Código)

**Archivo:** `compiler/codegen_java.py`

**Función:** Traduce AST/IR a código Java.

**Estrategia:**
- Mapeo directo desde nodos AST
- Preservación de estructura
- Generación de código válido Java

**Características:**
- Indentación automática
- Generación de bloques
- Manejo de expresiones complejas
- Soporte para arrays y métodos

### 3.7 Formatter (Formateador)

**Archivo:** `compiler/formatter_java.py`

**Función:** Formatea el código Java generado.

**Reglas de Formateo:**
- Espacios alrededor de operadores
- Indentación consistente
- Llaves en líneas separadas (opción K&R)
- Espaciado en parámetros de métodos

**Procesamiento:**
```java
// Antes
int x=5+3*2;

// Después
int x = 5 + 3 * 2;
```

---

## 4. FASES DE COMPILACIÓN

### 4.1 Fase 1: Análisis Léxico

**Entrada:** Texto fuente Java
**Salida:** Lista de tokens + diagnósticos léxicos

**Proceso:**
1. Lee caracteres secuencialmente
2. Agrupa en lexemas
3. Clasifica como tokens
4. Ignora espacios y comentarios
5. Reporta errores léxicos

**Errores Detectados:**
- Caracteres inválidos
- Literales mal formados
- Comentarios sin cerrar

### 4.2 Fase 2: Análisis Sintáctico

**Entrada:** Tokens
**Salida:** AST + diagnósticos sintácticos

**Proceso:**
1. Aplica gramática recursiva
2. Construye árbol jerárquico
3. Valida estructura del programa
4. Reporta errores sintácticos

**Errores Detectados:**
- Tokens inesperados
- Falta de delimitadores
- Estructura inválida

### 4.3 Fase 3: Análisis Semántico

**Entrada:** AST
**Salida:** AST tipado + tabla de símbolos + diagnósticos

**Proceso:**
1. Construye tabla de símbolos
2. Verifica tipos
3. Valida uso de variables
4. Comprueba control de flujo
5. Reporta errores semánticos

**Errores Detectados:**
- Tipos incompatibles
- Variables no declaradas
- Retornos faltantes
- Break/continue fuera de loops

### 4.4 Fase 4: Generación IR

**Entrada:** AST tipado
**Salida:** CFG + TAC + diagnósticos

**Proceso:**
1. Lineariza estructuras de control
2. Genera temporales
3. Construye CFG
4. Asigna etiquetas

### 4.5 Fase 5: Optimización

**Entrada:** IR
**Salida:** IR optimizado

**Proceso:**
1. Evalúa constantes
2. Propaga valores
3. Elimina código muerto
4. Simplifica expresiones

### 4.6 Fase 6: Generación de Código

**Entrada:** AST tipado
**Salida:** Código Java

**Proceso:**
1. Recorre AST
2. Emite código Java
3. Mantiene contexto de indentación

### 4.7 Fase 7: Formateo

**Entrada:** Código Java raw
**Salida:** Código Java formateado

**Proceso:**
1. Aplica reglas de espaciado
2. Corrige indentación
3. Formatea operadores

---

## 5. CARACTERÍSTICAS IMPLEMENTADAS

### 5.1 Tipos de Datos

| Tipo | Descripción | Tamaño | Ejemplo |
|------|-------------|--------|---------|
| `int` | Entero | 32 bits | `42` |
| `double` | Punto flotante | 64 bits | `3.14` |
| `boolean` | Lógico | 1 bit | `true` |
| `int[]` | Array de enteros | Variable | `new int[5]` |
| `double[]` | Array de doubles | Variable | `new double[10]` |

### 5.2 Operadores

**Aritméticos:**
- `+` : Suma
- `-` : Resta
- `*` : Multiplicación
- `/` : División entera/real
- Módulo simulado: `a - (a/b)*b`

**Comparación:**
- `==` : Igualdad
- `!=` : Desigualdad
- `<` : Menor que
- `>` : Mayor que
- `<=` : Menor o igual
- `>=` : Mayor o igual

**Lógicos:**
- `&&` : AND lógico
- `||` : OR lógico
- `!` : NOT lógico

**Asignación:**
- `=` : Asignación simple

### 5.3 Estructuras de Control

**Condicionales:**
```java
if (condicion) {
    // código
}

if (condicion) {
    // código
} else {
    // código alternativo
}
```

**Bucles:**
```java
while (condicion) {
    // código
}

for (inicializacion; condicion; actualizacion) {
    // código
}
```

**Control de Flujo:**
```java
break;      // Sale del loop
continue;   // Siguiente iteración
return valor; // Retorna de método
```

### 5.4 Métodos

**Declaración:**
```java
public static tipo nombre(parametros) {
    // cuerpo
}
```

**Características:**
- Parámetros tipados
- Tipos de retorno: void, int, double, boolean
- Recursión soportada
- Validación de aridad y tipos

**Ejemplo:**
```java
public static int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
```

### 5.5 Arrays

**Creación:**
```java
int[] arr = new int[10];
```

**Inicialización:**
```java
int[] primos = new int[]{2, 3, 5, 7, 11};
```

**Acceso:**
```java
int valor = arr[0];
arr[5] = 42;
```

**Como Parámetros:**
```java
public static int suma(int[] arr, int size) {
    // ...
}
```

### 5.6 Entrada/Salida

**Salida:**
```java
System.out.println(expresion);
```

Soporta: int, double, boolean, String (solo en println)

---

## 6. ESPECIFICACIONES TÉCNICAS

### 6.1 Gramática Formal

```bnf
<program> ::= <class-decl>

<class-decl> ::= "class" <id> "{" <method-decl>* "}"

<method-decl> ::= "public" "static" <type> <id> 
                  "(" <param-list>? ")" <block>

<param-list> ::= <type> <id> ("," <type> <id>)*

<type> ::= "void" | "int" | "double" | "boolean" | <type> "[]"

<block> ::= "{" <stmt>* "}"

<stmt> ::= <var-decl>
         | <assign-stmt>
         | <if-stmt>
         | <while-stmt>
         | <for-stmt>
         | <return-stmt>
         | <break-stmt>
         | <continue-stmt>
         | <expr-stmt>

<var-decl> ::= <type> <id> ("=" <expr>)? ";"

<if-stmt> ::= "if" "(" <expr> ")" <block> ("else" <block>)?

<while-stmt> ::= "while" "(" <expr> ")" <block>

<for-stmt> ::= "for" "(" <var-decl> <expr> ";" <expr> ")" <block>

<return-stmt> ::= "return" <expr>? ";"

<break-stmt> ::= "break" ";"

<continue-stmt> ::= "continue" ";"

<expr> ::= <logical-or>

<logical-or> ::= <logical-and> ("||" <logical-and>)*

<logical-and> ::= <equality> ("&&" <equality>)*

<equality> ::= <comparison> (("==" | "!=") <comparison>)*

<comparison> ::= <addition> (("<" | ">" | "<=" | ">=") <addition>)*

<addition> ::= <multiplication> (("+" | "-") <multiplication>)*

<multiplication> ::= <unary> (("*" | "/") <unary>)*

<unary> ::= ("!" | "-") <unary> | <postfix>

<postfix> ::= <primary> ("[" <expr> "]" | "(" <args>? ")")*

<primary> ::= <literal> | <id> | "(" <expr> ")" 
            | "new" <type> "[" <expr> "]"
            | "new" <type> "[" "]" "{" <expr-list> "}"
```

### 6.2 Precedencia de Operadores

| Nivel | Operadores | Asociatividad |
|-------|-----------|---------------|
| 1 (mayor) | `!`, `-` (unario) | Derecha |
| 2 | `*`, `/` | Izquierda |
| 3 | `+`, `-` | Izquierda |
| 4 | `<`, `>`, `<=`, `>=` | Izquierda |
| 5 | `==`, `!=` | Izquierda |
| 6 | `&&` | Izquierda |
| 7 (menor) | `||` | Izquierda |

### 6.3 Sistema de Tipos

**Reglas de Compatibilidad:**

1. Tipos idénticos siempre compatibles
2. `int` → `double` (conversión implícita)
3. `double` ↛ `int` (requiere cast explícito, no soportado)
4. `boolean` solo compatible con `boolean`
5. Arrays requieren tipo de elemento compatible

**Tabla de Conversiones:**

| De | A | Permitido |
|----|---|-----------|
| int | double | ✓ |
| double | int | ✗ |
| int | boolean | ✗ |
| boolean | int | ✗ |
| int[] | double[] | ✗ |

### 6.4 Gestión de Memoria

**Alcance de Variables:**
- Variables locales: scope de bloque
- Parámetros: scope de método
- No variables globales (solo métodos estáticos)

**Tabla de Símbolos:**
- Organizada por niveles de scope
- Búsqueda hacia arriba (shadowing)
- Liberación al salir de scope

---

## 7. MANEJO DE ERRORES

### 7.1 Sistema de Diagnósticos

**Estructura:**
```python
class Diagnostic:
    severity: str    # "error", "warning", "info"
    stage: str       # "lexer", "parser", "semantics", etc.
    message: str     # Descripción del error
    line: int        # Línea del error
    col: int         # Columna del error
    code: str        # Código de error
```

### 7.2 Tipos de Errores

**Errores Léxicos:**
- Caracteres inválidos
- Literales mal formados
- Comentarios sin cerrar

**Errores Sintácticos:**
- Tokens inesperados
- Falta de `;`, `}`, `)`, etc.
- Estructura inválida

**Errores Semánticos:**
- Variables no declaradas
- Tipos incompatibles
- Métodos no encontrados
- Aridad incorrecta
- Return faltante en métodos no-void
- Break/continue fuera de loops
- Índices de array no enteros

### 7.3 Recuperación de Errores

**Estrategias:**
1. **Modo pánico:** Sincronización en delimitadores (`;`, `}`)
2. **Producción de error:** Genera nodo de error en AST
3. **Continuación:** Intenta seguir compilando tras error

---

## 8. OPTIMIZACIONES

### 8.1 Optimizaciones Implementadas (O1)

**1. Constant Folding:**
```
Antes:  x = 2 + 3
Después: x = 5
```

**2. Constant Propagation:**
```
Antes:  x = 5; y = x + 2
Después: x = 5; y = 7
```

**3. Dead Code Elimination:**
```
Antes:  t0 = 5; (t0 nunca usado)
Después: (eliminado)
```

**4. Algebraic Simplification:**
```
x * 1  →  x
x + 0  →  x
x - 0  →  x
x * 0  →  0
0 + x  →  x
```

### 8.2 Métricas de Optimización

**Medidas de Eficacia:**
- Reducción de instrucciones IR
- Eliminación de temporales
- Evaluación en tiempo de compilación

**Ejemplo Completo:**
```java
// Original
int a = 5;
int b = 3;
int c = a + b * 2 + 0;

// Después de O1
int a = 5;
int b = 3;
int c = 11;
```

---

## 9. LIMITACIONES Y RESTRICCIONES

### 9.1 Características No Soportadas

| Característica | Soporte | Workaround |
|----------------|---------|------------|
| Operador `%` | ✗ | `a - (a/b)*b` |
| Operador `++` | ✗ | `i = i + 1` |
| Operador `+=` | ✗ | `x = x + 5` |
| Switch/case | ✗ | Usar if-else |
| do-while | ✗ | Usar while |
| Strings como tipo | ✗ | Solo en println |
| Arrays multidimensionales | ✗ | - |
| Clases múltiples | ✗ | - |
| Métodos no-estáticos | ✗ | - |
| Herencia | ✗ | - |
| Interfaces | ✗ | - |
| Excepciones | ✗ | - |
| Generics | ✗ | - |

### 9.2 Restricciones de Diseño

**Arquitectura:**
- Una sola clase por archivo
- Todos los métodos deben ser `public static`
- Método `main` obligatorio para ejecución

**Sintaxis:**
- Llaves obligatorias en bloques
- Punto y coma obligatorio
- Tipos explícitos (no inferencia)

---

## 10. PRUEBAS Y VALIDACIÓN

### 10.1 Suite de Pruebas

**Pruebas Unitarias:**
- `test_lexer.py`: 20+ casos de tokenización
- `test_parser.py`: 30+ casos de parsing
- `test_semantics.py`: 25+ casos de validación semántica
- `test_ir.py`: 15+ casos de generación IR
- `test_optimizer.py`: 20+ casos de optimización
- `test_codegen_java.py`: 25+ casos de generación
- `test_formatter_java.py`: 15+ casos de formateo

**Pruebas de Integración:**
- Ejemplos completos end-to-end
- Compilación y ejecución con javac/java
- Validación de salida esperada

### 10.2 Ejemplos de Validación

**Conjunto de Ejemplos:**
1. `ejemplo_basico.java`: Variables y operaciones
2. `ejemplo_condicionales.java`: If/else y operadores lógicos
3. `ejemplo_loops.java`: While, for, break, continue
4. `ejemplo_metodos.java`: Métodos y recursión
5. `ejemplo_arrays.java`: Arrays y manipulación
6. `ejemplo_completo.java`: Fibonacci, ordenamiento, búsqueda
7. `ejemplo_matematicas.java`: MCD, primos, potencias

**Criterios de Validación:**
- Compilación sin errores
- Ejecución correcta con javac/java
- Salida esperada coincide
- Diagnósticos informativos en errores

### 10.3 Cobertura de Código

**Áreas Cubiertas:**
- ✓ Todos los tipos de datos
- ✓ Todos los operadores
- ✓ Todas las estructuras de control
- ✓ Métodos con parámetros y recursión
- ✓ Arrays (creación, acceso, modificación)
- ✓ Break y continue
- ✓ Return statements
- ✓ Validación semántica completa
- ✓ Optimizaciones O1

---

## APÉNDICES

### A. Tabla de Tokens

| Token | Descripción | Ejemplo |
|-------|-------------|---------|
| `CLASS` | Palabra clave class | `class` |
| `PUBLIC` | Modificador public | `public` |
| `STATIC` | Modificador static | `static` |
| `VOID` | Tipo void | `void` |
| `INT_T` | Tipo int | `int` |
| `DOUBLE_T` | Tipo double | `double` |
| `BOOLEAN_T` | Tipo boolean | `boolean` |
| `IF` | Condicional if | `if` |
| `ELSE` | Condicional else | `else` |
| `WHILE` | Bucle while | `while` |
| `FOR` | Bucle for | `for` |
| `RETURN` | Return statement | `return` |
| `BREAK` | Break statement | `break` |
| `CONTINUE` | Continue statement | `continue` |
| `NEW` | Operador new | `new` |
| `TRUE` | Literal booleano | `true` |
| `FALSE` | Literal booleano | `false` |
| `IDENT` | Identificador | `myVar` |
| `INT_LIT` | Literal entero | `42` |
| `DOUBLE_LIT` | Literal double | `3.14` |
| `PLUS` | Operador suma | `+` |
| `MINUS` | Operador resta | `-` |
| `STAR` | Operador multiplicación | `*` |
| `SLASH` | Operador división | `/` |
| `EQ` | Operador igualdad | `==` |
| `NE` | Operador desigualdad | `!=` |
| `LT` | Operador menor | `<` |
| `GT` | Operador mayor | `>` |
| `LE` | Operador menor-igual | `<=` |
| `GE` | Operador mayor-igual | `>=` |
| `AND` | Operador AND lógico | `&&` |
| `OR` | Operador OR lógico | `||` |
| `NOT` | Operador NOT lógico | `!` |
| `ASSIGN` | Asignación | `=` |
| `LPAREN` | Paréntesis izquierdo | `(` |
| `RPAREN` | Paréntesis derecho | `)` |
| `LBRACE` | Llave izquierda | `{` |
| `RBRACE` | Llave derecha | `}` |
| `LBRACK` | Corchete izquierdo | `[` |
| `RBRACK` | Corchete derecho | `]` |
| `SEMICOLON` | Punto y coma | `;` |
| `COMMA` | Coma | `,` |
| `DOT` | Punto | `.` |

### B. Códigos de Error

| Código | Descripción | Ejemplo |
|--------|-------------|---------|
| `LEXER_INVALID_CHAR` | Carácter inválido | `@` en el código |
| `PARSER_UNEXPECTED_TOKEN` | Token inesperado | Falta `;` |
| `SEM_UNDEFINED_VAR` | Variable no declarada | Uso antes de declarar |
| `SEM_TYPE_MISMATCH` | Tipos incompatibles | `int = boolean` |
| `SEM_UNDEFINED_METHOD` | Método no existe | Llamada a método inexistente |
| `SEM_ARITY_MISMATCH` | Número de argumentos incorrecto | `func(1, 2)` espera 3 |
| `SEM_RETURN_MISSING` | Falta return | Método no-void sin return |
| `SEM_BREAK_OUTSIDE_LOOP` | Break fuera de loop | `break;` en método |
| `SEM_ARRAY_INDEX_TYPE` | Índice no entero | `arr[3.14]` |

### C. Formato de Salida JSON

**Estructura de Diagnóstico:**
```json
{
  "severity": "error",
  "stage": "semantics",
  "message": "Variable 'x' no declarada",
  "line": 5,
  "col": 10,
  "end_line": 5,
  "end_col": 11,
  "code": "SEM_UNDEFINED_VAR"
}
```

**Resultado de Compilación:**
```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "javaCode": "...",
  "logs": ["lexer: ok", "parser: ok", ...],
  "timeMs": 45
}
```

---

**Versión:** 1.0
**Fecha:** Noviembre 2025
**Autor:** Yahir750
**Lenguaje de Implementación:** Python 3.x
**Líneas de Código:** ~5000
