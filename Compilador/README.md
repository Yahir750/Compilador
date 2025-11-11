# Compilador Java → Java

Un compilador completo que traduce código Java a código Java optimizado, implementando todas las fases tradicionales de compilación.

---

## Descripción

Este proyecto es un compilador educativo pero completamente funcional que procesa código Java a través de análisis léxico, sintáctico, semántico, generación de representación intermedia, optimización y generación de código final formateado.

### Características Principales

- **Pipeline completo de compilación** con 7 fases
- **Interfaz gráfica** con syntax highlighting y números de línea
- **Optimizaciones automáticas** (constant folding, dead code elimination, etc.)
- **Sistema de diagnósticos** detallado con ubicación precisa de errores
- **Soporte para recursión** y estructuras de control avanzadas
- **Validación semántica completa** con tabla de símbolos
- **Suite de pruebas** y ejemplos listos para ejecutar

---

## Instalación Rápida

### Requisitos

- Python 3.8+
- JDK 8+

### Pasos

```bash
# Clonar repositorio
git clone https://github.com/Yahir750/Compilador.git
cd Compilador

# Verificar instalación
python --version
java -version
javac -version
```

---

## Uso

### Interfaz Gráfica (Recomendado)

```bash
python main.py --gui
```

![Captura de GUI](docs/gui_screenshot.png)

### Línea de Comandos

```bash
# Compilación básica
python main.py archivo.java -o salida.java

# Con optimizaciones
python main.py archivo.java --O1 -o salida.java

# Ver AST
python main.py archivo.java --ast

# Ver IR
python main.py archivo.java --ir
```

---

## Características Soportadas

### Tipos de Datos
- `int`, `double`, `boolean`
- Arrays: `int[]`, `double[]`

### Operadores
- Aritméticos: `+`, `-`, `*`, `/`
- Comparación: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Lógicos: `&&`, `||`, `!`

### Estructuras de Control
- `if`, `if-else`
- `while`, `for`
- `break`, `continue`, `return`

### Métodos
- Métodos estáticos con parámetros
- Recursión completa
- Validación de tipos y aridad

### Arrays
- Creación: `new int[10]`
- Inicialización: `new int[]{1,2,3}`
- Acceso y modificación

---

## Ejemplos

```java
// Factorial recursivo
public class Factorial {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
    
    public static void main(String[] args) {
        System.out.println(factorial(5));  // 120
    }
}
```

Más ejemplos en la carpeta `examples/`:
- `ejemplo_basico.java` - Variables y operaciones
- `ejemplo_metodos.java` - Métodos y recursión
- `ejemplo_arrays.java` - Manipulación de arrays
- `ejemplo_completo.java` - Fibonacci, ordenamiento, búsqueda
- `ejemplo_matematicas.java` - MCD, primos, potencias

---

## Arquitectura

```
Código Fuente
    ↓
[LEXER] → Tokens
    ↓
[PARSER] → AST
    ↓
[SEMANTICS] → AST Tipado + Símbolos
    ↓
[IR] → Control Flow Graph
    ↓
[OPTIMIZER] → IR Optimizado
    ↓
[CODEGEN] → Código Java
    ↓
[FORMATTER] → Código Final
```

---

## Documentación

- **[DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md)** - Especificaciones técnicas completas
- **[MANUAL_USUARIO.md](MANUAL_USUARIO.md)** - Guía de uso detallada
- **[GUION_VIDEO.md](GUION_VIDEO.md)** - Script para presentación en video
- **[examples/EJEMPLOS_README.md](examples/EJEMPLOS_README.md)** - Guía de ejemplos

---

## Pruebas

### Ejecutar Suite Completa

```bash
# PowerShell
.\probar_ejemplos.ps1

# Bash
./probar_ejemplos.sh
```

### Pruebas Unitarias

```bash
python -m pytest tests/
```

---

## Optimizaciones

### Nivel O0 (Sin optimización)
Código generado tal cual sin modificaciones.

### Nivel O1 (Optimizaciones locales)
- **Constant folding**: `2 + 3` → `5`
- **Constant propagation**: Propaga valores constantes
- **Dead code elimination**: Elimina código no utilizado
- **Algebraic simplification**: `x * 1` → `x`, `x + 0` → `x`

---

## Estructura del Proyecto

```
Compilador/
├── compiler/              # Núcleo del compilador
│   ├── lexer.py          # Análisis léxico
│   ├── parser.py         # Análisis sintáctico
│   ├── ast_nodes.py      # Nodos del AST
│   ├── semantics.py      # Análisis semántico
│   ├── ir.py             # Representación intermedia
│   ├── optimizer.py      # Optimizador
│   ├── codegen_java.py   # Generador de código
│   ├── formatter_java.py # Formateador
│   └── diagnostics.py    # Sistema de errores
├── utils/                # Utilidades
│   ├── tokens.py         # Definición de tokens
│   ├── symbols.py        # Tabla de símbolos
│   ├── config.py         # Configuración
│   └── visitors.py       # Patrones visitor
├── gui/                  # Interfaz gráfica
│   ├── app.py           # Aplicación GUI
│   └── components.py    # Componentes
├── tests/               # Suite de pruebas
├── examples/            # Ejemplos de código
├── main.py             # Punto de entrada
└── pyproject.toml      # Configuración Python
```

---

## Limitaciones Conocidas

| Característica | Soportado | Workaround |
|----------------|-----------|------------|
| Operador `%` | ❌ | `a - (a/b)*b` |
| Operador `++` | ❌ | `i = i + 1` |
| Operador `+=` | ❌ | `x = x + 5` |
| Switch/case | ❌ | Usar if-else |
| Strings como tipo | ❌ | Solo en println |
| Arrays multidimensionales | ❌ | - |
| Herencia/Interfaces | ❌ | - |

---

## Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agrega nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

---

## Roadmap

### Versión 1.1 (Futuro)
- [ ] Soporte para Strings como tipo completo
- [ ] Arrays multidimensionales
- [ ] Operador módulo nativo
- [ ] Switch/case
- [ ] Do-while loops

### Versión 2.0 (Futuro)
- [ ] Clases múltiples
- [ ] Métodos no estáticos
- [ ] Herencia básica
- [ ] Más optimizaciones (loop unrolling, inlining)

---

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## Autores

- **Yahir750** - *Desarrollo principal* - [GitHub](https://github.com/Yahir750)

---

## Agradecimientos

- Inspirado en los principios de compiladores tradicionales
- Diseñado con propósitos educativos
- Implementa conceptos de "Compilers: Principles, Techniques, and Tools" (Dragon Book)

---

## Contacto

- **GitHub Issues**: [https://github.com/Yahir750/Compilador/issues](https://github.com/Yahir750/Compilador/issues)
- **Repositorio**: [https://github.com/Yahir750/Compilador](https://github.com/Yahir750/Compilador)

---

## Estadísticas del Proyecto

- **Líneas de código**: ~5,000
- **Lenguaje**: Python 3.x
- **Fases de compilación**: 7
- **Ejemplos incluidos**: 7
- **Pruebas unitarias**: 100+
- **Cobertura**: Todas las características implementadas

---

**Versión**: 1.0
**Estado**: Estable
**Última actualización**: Noviembre 2025
