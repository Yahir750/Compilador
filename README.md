# Compilador

Proyecto para construir un **compilador** desde cero en Java.

## ¿Qué es este proyecto?
Este repositorio contiene la implementación de un compilador que toma código fuente escrito en un lenguaje definido para el proyecto y lo **analiza** para producir una salida equivalente (por ejemplo: ejecución/evaluación, generación de código intermedio o validación del programa).

## ¿Para qué sirve?
- **Aprender y practicar** los componentes de un compilador: análisis léxico, análisis sintáctico y análisis semántico.
- **Procesar programas** del lenguaje objetivo para detectar errores y/o ejecutar instrucciones.
- Servir como **base** para extender el lenguaje y agregar características (nuevas reglas, tipos, operadores, etc.).

## Características (alto nivel)
- Tokenización (lexer)
- Parser (gramática/árbol de análisis)
- Validaciones semánticas básicas (según el alcance del proyecto)
- Ejecución o generación de salida (según la implementación)

## Estructura del repositorio
La organización de carpetas/archivos puede variar según iteraciones del proyecto. Revisa el código fuente para identificar los módulos principales (lexer/parser/AST/ejecución).

## Uso
Consulta el código y/o scripts del repositorio para ver cómo compilar/ejecutar el proyecto y cómo proporcionar un archivo de entrada al compilador.
