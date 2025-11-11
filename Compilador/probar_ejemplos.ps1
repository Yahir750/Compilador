# Script PowerShell para probar todos los ejemplos del compilador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   COMPILADOR JAVA - PRUEBA DE EJEMPLOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Crear carpeta output si no existe
if (!(Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
}

$ejemplos = @(
    "ejemplo_basico",
    "ejemplo_condicionales",
    "ejemplo_loops",
    "ejemplo_metodos",
    "ejemplo_arrays",
    "ejemplo_completo",
    "ejemplo_matematicas"
)

$total = $ejemplos.Length
$exitosos = 0
$fallidos = 0

for ($i = 0; $i -lt $total; $i++) {
    $ejemplo = $ejemplos[$i]
    $num = $i + 1
    
    Write-Host "[$num/$total] Probando $ejemplo.java..." -ForegroundColor Yellow
    
    # Capitalizar nombre para la clase
    $className = (Get-Culture).TextInfo.ToTitleCase($ejemplo)
    $className = $className -replace "_", ""
    
    # Compilar
    python main.py "examples/$ejemplo.java" -o "output/$className.java" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        # Compilar con javac
        Set-Location output
        javac "$className.java" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Compilación exitosa" -ForegroundColor Green
            Write-Host "  Salida:" -ForegroundColor White
            java $className
            $exitosos++
        } else {
            Write-Host "  ✗ Error en javac" -ForegroundColor Red
            $fallidos++
        }
        
        Set-Location ..
    } else {
        Write-Host "  ✗ Error en compilador" -ForegroundColor Red
        $fallidos++
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "           RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Exitosos: $exitosos/$total" -ForegroundColor Green
Write-Host "Fallidos:  $fallidos/$total" -ForegroundColor $(if ($fallidos -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
