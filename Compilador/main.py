from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import is_dataclass, asdict
from typing import Any, Tuple

from compiler import lexer, parser, semantics, ir, optimizer, codegen_java, diagnostics
from compiler.formatter_java import format_java


# --------------------------
# Utilidades de serialización
# --------------------------

def _to_jsonable(obj: Any) -> Any:
    """
    Convierte dataclasses (AST/IR/Diagnostic) en estructuras JSON-compatibles.
    Maneja tuplas -> listas para evitar sorpresas al serializar.
    """
    if is_dataclass(obj):
        d = asdict(obj)
        return _to_jsonable(d)
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    return obj


def _collect(diags):
    errs = [d for d in diags if d.severity == "error"]
    warns = [d for d in diags if d.severity == "warning"]
    return errs, warns


# --------------------------
# Orquestador principal
# --------------------------

def compile_java_text(src: str, opt_level: int = 0, mode: str = "default") -> Tuple[dict, int]:
    """
    Ejecuta: lexer → parser → semantics → (IR → optimizer) → codegen → formatter
    Retorna (resultado_json, exit_code)
    """
    logs = []
    all_errors = []
    all_warnings = []

    t0 = time.perf_counter()

    try:
        # LÉXICO
        toks, dlex = lexer.lex(src)
        logs.append("lexer: ok")
        e, w = _collect(dlex)
        all_errors += e
        all_warnings += w

        # PARSER
        ast, dpar = parser.parse(toks)
        logs.append("parser: ok")
        e, w = _collect(dpar)
        all_errors += e
        all_warnings += w

        # SEMÁNTICA
        if not any(d.severity == "error" for d in all_errors):
            ast_typed, dsem, _ = semantics.analyze(ast)
            logs.append("semantics: ok")
            e, w = _collect(dsem)
            all_errors += e
            all_warnings += w
        else:
            ast_typed = ast

        ir_prog = None
        # IR + OPT
        if not any(d.severity == "error" for d in all_errors) and mode in ("default", "ir"):
            ir_prog, dir_ = ir.lower(ast_typed)
            logs.append("ir: ok")
            e, w = _collect(dir_)
            all_errors += e
            all_warnings += w

            if not any(d.severity == "error" for d in all_errors) and opt_level > 0:
                ir_prog, dopt = optimizer.optimize(ir_prog, level=opt_level)
                logs.append(f"optimizer: O{opt_level}")
                # optimizer no debería emitir errores, solo warnings/info
                e, w = _collect(dopt)
                all_errors += e
                all_warnings += w

        result_payload = {}
        java_out = ""

        # MODO AST/IR (depuración)
        if mode == "ast":
            result_payload = {"ast": _to_jsonable(ast_typed)}
        elif mode == "ir":
            result_payload = {"ir": _to_jsonable(ir_prog) if ir_prog else {}}
        else:
            # CODEGEN + FORMATTER (solo si no hay errores)
            if not any(d.severity == "error" for d in all_errors):
                java_raw, dcg = codegen_java.emit(ast_typed, from_stage="ast")
                logs.append("codegen: ok")
                _, w = _collect(dcg)
                all_warnings += w

                java_fmt, dfmt = format_java(java_raw)
                logs.append("formatter: ok")
                _, w = _collect(dfmt)
                all_warnings += w

                java_out = java_fmt

        ok = len([d for d in all_errors if d.severity == "error"]) == 0
        time_ms = int((time.perf_counter() - t0) * 1000)

        result = {
            "ok": ok,
            "errors": diagnostics.to_json(all_errors),
            "warnings": diagnostics.to_json(all_warnings),
            "javaCode": java_out if (ok and mode == "default") else "",
            "logs": logs,
            "timeMs": time_ms,
        }
        # Mezcla payload (ast/ir) si corresponde
        result.update(result_payload)

        return result, (0 if ok else 1)

    except Exception as ex:
        time_ms = int((time.perf_counter() - t0) * 1000)
        # fallo interno → código 2
        err = diagnostics.Diagnostic(
            severity="error",
            stage="orchestrator",
            message=f"Fallo interno: {ex.__class__.__name__}: {ex}",
            line=0, col=0, end_line=0, end_col=0,
            code="INTERNAL_ERROR",
        )
        result = {
            "ok": False,
            "errors": diagnostics.to_json([err]),
            "warnings": [],
            "javaCode": "",
            "logs": logs + ["orchestrator: exception"],
            "timeMs": time_ms,
        }
        return result, 2


# --------------------------
# CLI
# --------------------------

def main() -> int:
    ap = argparse.ArgumentParser(prog="java2java", description="Java→Java compiler (v1)")
    ap.add_argument("input", nargs="?", help="Archivo .java (si se omite, usa stdin; si no hay input abre GUI con --gui)")
    ap.add_argument("-o", "--output", help="Archivo de salida .java")
    ap.add_argument("--O0", action="store_true", help="Sin optimizaciones")
    ap.add_argument("--O1", action="store_true", help="Optimizaciones locales (peephole)")
    ap.add_argument("--ast", action="store_true", help="Salida de AST en JSON (depuración)")
    ap.add_argument("--ir", action="store_true", help="Salida de IR en JSON (depuración)")
    ap.add_argument("--json", action="store_true", help="Imprime el objeto JSON del contrato")
    ap.add_argument("--gui", action="store_true", help="Abrir GUI (fase 10)")

    args = ap.parse_args()

    # GUI (fase 10)
    if args.gui and not args.input and sys.stdin.isatty():
        try:
            from gui.app import run_gui
        except Exception:
            print("GUI no disponible en esta fase. Quita --gui o pasa un archivo de entrada.", file=sys.stderr)
            return 2
        run_gui()
        return 0

    # Leer fuente
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            src = f.read()
    else:
        if sys.stdin.isatty():
            print("Leyendo de stdin: pega el código Java y presiona Ctrl+D (Linux/mac) o Ctrl+Z (Windows).", file=sys.stderr)
        src = sys.stdin.read()

    # Modo
    mode = "default"
    if args.ast:
        mode = "ast"
    if args.ir:
        mode = "ir"

    opt_level = 1 if args.O1 else 0  # O0 por defecto
    result, code = compile_java_text(src, opt_level=opt_level, mode=mode)

    # Escribir archivo de salida .java si procede
    if args.output and result.get("javaCode"):
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result["javaCode"])

    # Imprimir resultado
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if mode == "default":
            # imprime Java o errores legibles si hay
            if result["ok"]:
                print(result["javaCode"], end="")
            else:
                # muestra JSON mínimo con errores para no perder detalle
                print(json.dumps({
                    "ok": False,
                    "errors": result["errors"],
                    "warnings": result["warnings"],
                }, ensure_ascii=False, indent=2))
        else:
            # AST/IR
            key = "ast" if mode == "ast" else "ir"
            print(json.dumps(result.get(key, {}), ensure_ascii=False, indent=2))

    return code


if __name__ == "__main__":
    sys.exit(main())
