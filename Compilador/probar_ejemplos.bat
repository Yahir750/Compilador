@echo off
REM Script para probar todos los ejemplos del compilador
echo ========================================
echo    COMPILADOR JAVA - PRUEBA DE EJEMPLOS
echo ========================================
echo.

REM Crear carpeta output si no existe
if not exist "output" mkdir output

echo [1/7] Probando ejemplo_basico.java...
python main.py examples/ejemplo_basico.java -o output/EjemploBasico.java
cd output
javac EjemploBasico.java
echo Salida:
java EjemploBasico
cd ..
echo.

echo [2/7] Probando ejemplo_condicionales.java...
python main.py examples/ejemplo_condicionales.java -o output/EjemploCondicionales.java
cd output
javac EjemploCondicionales.java
echo Salida:
java EjemploCondicionales
cd ..
echo.

echo [3/7] Probando ejemplo_loops.java...
python main.py examples/ejemplo_loops.java -o output/EjemploLoops.java
cd output
javac EjemploLoops.java
echo Salida:
java EjemploLoops
cd ..
echo.

echo [4/7] Probando ejemplo_metodos.java...
python main.py examples/ejemplo_metodos.java -o output/EjemploMetodos.java
cd output
javac EjemploMetodos.java
echo Salida:
java EjemploMetodos
cd ..
echo.

echo [5/7] Probando ejemplo_arrays.java...
python main.py examples/ejemplo_arrays.java -o output/EjemploArrays.java
cd output
javac EjemploArrays.java
echo Salida:
java EjemploArrays
cd ..
echo.

echo [6/7] Probando ejemplo_completo.java...
python main.py examples/ejemplo_completo.java -o output/EjemploCompleto.java
cd output
javac EjemploCompleto.java
echo Salida:
java EjemploCompleto
cd ..
echo.

echo [7/7] Probando ejemplo_matematicas.java...
python main.py examples/ejemplo_matematicas.java -o output/EjemploMatematicas.java
cd output
javac EjemploMatematicas.java
echo Salida:
java EjemploMatematicas
cd ..
echo.

echo ========================================
echo      TODAS LAS PRUEBAS COMPLETADAS
echo ========================================
pause
