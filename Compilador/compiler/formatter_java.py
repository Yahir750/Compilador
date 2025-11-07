import re
from typing import Tuple, List
from compiler.diagnostics import Diagnostic

def format_java(java_src: str) -> Tuple[str, List[Diagnostic]]:
    """
    Formatea código Java fuente de forma simple (estilo K&R).
    No cambia semántica, solo espaciado y sangría.
    """
    diags: List[Diagnostic] = []

    # Normaliza saltos de línea
    src = java_src.replace("\r\n", "\n").replace("\r", "\n").strip()

    # Espacios consistentes alrededor de operadores
    # (solo los más comunes; evita los de cadenas o comentarios)
    src = re.sub(r"(?<!\w)=(?![=>])", " = ", src)
    src = re.sub(r"(?<![=!<>])==(?!=)", " == ", src)
    src = re.sub(r"(?<![=!<>])!=(?!=)", " != ", src)
    src = re.sub(r"(?<!\w)\+(?!\+|\=)", " + ", src)
    src = re.sub(r"(?<!\w)\-(?!\-|\=)", " - ", src)
    src = re.sub(r"(?<!\w)\*(?!\=)", " * ", src)
    src = re.sub(r"(?<!\w)/(?!\=)", " / ", src)
    src = re.sub(r"(?<!\w)<(?!<|=)", " < ", src)
    src = re.sub(r"(?<!\w)>(?!>|=)", " > ", src)
    src = re.sub(r"\s+", " ", src)  # colapsa múltiples espacios intermedios
    src = re.sub(r"\s*([;,\(\)\{\}])\s*", r"\1", src)  # limpia espacios dentro de paréntesis y llaves

    # Recoloca saltos de línea después de llaves, punto y coma
    src = src.replace(";", ";\n")
    src = src.replace("{", " {\n")
    src = src.replace("}", "}\n")

    # Añade salto de línea tras cada "else"
    src = re.sub(r"\}\s*else", "}\nelse", src)

    # Tokeniza por líneas y ajusta sangrías según llaves
    formatted_lines: List[str] = []
    indent = 0
    for raw_line in src.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        # Decrease indent before printing '}' line
        if line.startswith("}"):
            indent = max(0, indent - 1)
        formatted_lines.append("    " * indent + line)
        if line.endswith("{"):
            indent += 1

    # Une líneas, asegura salto final
    result = "\n".join(formatted_lines).rstrip() + "\n"

    # Opcional: recorta líneas >100 col (rudimentario)
    long_lines = [i + 1 for i, l in enumerate(formatted_lines) if len(l) > 100]
    for ln in long_lines:
        diags.append(Diagnostic(
            severity="warning",
            stage="formatter",
            message=f"Línea {ln} supera 100 caracteres (estilo)",
            line=ln,
            col=100,
            end_line=ln,
            end_col=len(formatted_lines[ln-1]),
            code="FMT_LINE_TOO_LONG"
        ))

    return result, diags
