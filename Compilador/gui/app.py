from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Tuple
import subprocess
import tempfile
import os

from compiler import lexer, parser, semantics, ir, optimizer, codegen_java, diagnostics
from compiler.formatter_java import format_java

APP_TITLE = "JavaToJavaCompiler GUI (v2) — Ejecutable"

# ============================================================
# Helpers visuales
# ============================================================
def _text_goto(text: tk.Text, line: int, col: int) -> None:
    # Tk Text indices are 1-based for lines, 0-based for columns in index string,
    # pero el usuario suele dar columnas 1-based, así que restamos 1 con seguridad.
    col_index = max(col - 1, 0)
    text.mark_set("insert", f"{line}.{col_index}")
    text.see(f"{line}.0")
    text.focus_set()

def _clear_tags(text: tk.Text) -> None:
    for tag in text.tag_names():
        text.tag_remove(tag, "1.0", "end")

def _highlight_line(text: tk.Text, line: int, tag="highlight_line"):
    _clear_tags(text)
    text.tag_configure(tag, background="#fff3cd")
    text.tag_add(tag, f"{line}.0", f"{line}.0 lineend")

def _set_theme(root: tk.Tk, dark: bool):
    bg = "#1e1e1e" if dark else "#ffffff"
    fg = "#d4d4d4" if dark else "#000000"
    panel_bg = "#252526" if dark else "#f3f3f3"
    accent = "#0e639c" if dark else "#0c63e4"

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=panel_bg)
    style.configure("TFrame", background=panel_bg)
    style.configure("TLabel", background=panel_bg, foreground=fg)
    # Notar: ttk.Button no siempre respeta background en todos los sistemas,
    # pero dejamos la configuración para aquellos que sí lo acepten.
    style.configure("TButton", foreground="#ffffff", relief="flat", padding=6)
    style.map("TButton", background=[("active", "#1177bb")])

    for w in root.winfo_children():
        _apply_widget_colors(w, bg, fg, panel_bg)

def _apply_widget_colors(widget, bg, fg, panel_bg):
    # Aplicar colores a widgets tkinter nativos, y propagar recursivamente.
    try:
        if isinstance(widget, tk.Text):
            widget.configure(bg=bg, fg=fg, insertbackground=fg, highlightbackground=panel_bg)
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg="#fafafa", fg="#000000")
    except Exception:
        # no nos detenemos por widgets que no acepten ciertas opciones
        pass

    for child in widget.winfo_children():
        _apply_widget_colors(child, bg, fg, panel_bg)

# ============================================================
# Compilador interno
# ============================================================
def _compile_pipeline(src: str, opt_level: int = 0, mode: str = "default"):
    logs: List[str] = []
    errors: List = []
    warnings: List = []

    toks, dlex = lexer.lex(src)
    logs.append("lexer: ok")
    errors += [d for d in dlex if getattr(d, "severity", "") == "error"]
    warnings += [d for d in dlex if getattr(d, "severity", "") == "warning"]

    ast, dpar = parser.parse(toks)
    logs.append("parser: ok")
    errors += [d for d in dpar if getattr(d, "severity", "") == "error"]
    warnings += [d for d in dpar if getattr(d, "severity", "") == "warning"]

    if not errors:
        ast_typed, dsem, _ = semantics.analyze(ast)
        logs.append("semantics: ok")
        errors += [d for d in dsem if getattr(d, "severity", "") == "error"]
        warnings += [d for d in dsem if getattr(d, "severity", "") == "warning"]
    else:
        ast_typed = ast

    ir_prog = None
    if not errors and mode in ("default", "ir"):
        ir_prog, dir_ = ir.lower(ast_typed)
        logs.append("ir: ok")
        errors += [d for d in dir_ if getattr(d, "severity", "") == "error"]
        warnings += [d for d in dir_ if getattr(d, "severity", "") == "warning"]

        if not errors and opt_level > 0:
            ir_prog, dopt = optimizer.optimize(ir_prog, level=opt_level)
            logs.append(f"optimizer: O{opt_level}")
            warnings += [d for d in dopt if getattr(d, "severity", "") == "warning"]

    java_out = ""
    if not errors and mode == "default":
        java_raw, dcg = codegen_java.emit(ast_typed, from_stage="ast")
        logs.append("codegen: ok")
        warnings += [d for d in dcg if getattr(d, "severity", "") == "warning"]

        java_fmt, dfmt = format_java(java_raw)
        logs.append("formatter: ok")
        warnings += [d for d in dfmt if getattr(d, "severity", "") == "warning"]
        java_out = java_fmt

    return {
        "ok": not errors,
        "errors": diagnostics.to_json(errors),
        "warnings": diagnostics.to_json(warnings),
        "javaCode": java_out,
        "ast": ast_typed,
        "ir": ir_prog,
        "logs": logs,
    }

# ============================================================
# GUI principal
# ============================================================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.dark_mode = tk.BooleanVar(value=False)
        self.opt_level = tk.IntVar(value=0)
        self.view_mode = tk.StringVar(value="default")

        outer = ttk.Frame(root, padding=8)
        outer.pack(fill="both", expand=True)

        # Barra superior de herramientas
        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(0, 6))

        ttk.Button(toolbar, text="Abrir .java", command=self._open_file).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Guardar salida", command=self._save_output).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Compilar", command=self._compile).pack(side="left", padx=3)
        ttk.Button(toolbar, text="▶ Ejecutar", command=self._run_java).pack(side="left", padx=8)

        ttk.Label(toolbar, text="Opt:").pack(side="left")
        ttk.Radiobutton(toolbar, text="O0", variable=self.opt_level, value=0).pack(side="left")
        ttk.Radiobutton(toolbar, text="O1", variable=self.opt_level, value=1).pack(side="left", padx=5)

        ttk.Label(toolbar, text="Vista:").pack(side="left")
        ttk.Radiobutton(toolbar, text="Java", variable=self.view_mode, value="default", command=self._compile).pack(side="left")
        ttk.Radiobutton(toolbar, text="AST", variable=self.view_mode, value="ast", command=self._compile).pack(side="left")
        ttk.Radiobutton(toolbar, text="IR", variable=self.view_mode, value="ir", command=self._compile).pack(side="left", padx=5)

        ttk.Checkbutton(toolbar, text="Modo oscuro", variable=self.dark_mode, command=self._apply_theme).pack(side="left")

        # Área central (editor + salida)
        middle = ttk.Panedwindow(outer, orient="horizontal")
        middle.pack(fill="both", expand=True, pady=6)

        left_frame = ttk.Frame(middle)
        self.editor = tk.Text(left_frame, wrap="none", undo=True, font=("Consolas", 11))
        self.editor.pack(fill="both", expand=True)
        middle.add(left_frame, weight=3)

        right_frame = ttk.Frame(middle)
        self.output = tk.Text(right_frame, wrap="none", state="normal", font=("Consolas", 11))
        self.output.pack(fill="both", expand=True)
        middle.add(right_frame, weight=3)

        # Panel inferior (diagnósticos + consola)
        bottom = ttk.Frame(outer)
        bottom.pack(fill="both", expand=False, pady=(6, 0))
        ttk.Label(bottom, text="Diagnósticos / Consola:").pack(anchor="w")

        self.diag_list = tk.Listbox(bottom, height=6, bg="#fafafa", font=("Consolas", 10))
        self.diag_list.pack(fill="x", expand=False)
        self.diag_list.bind("<<ListboxSelect>>", self._jump_to_diag)

        # Texto inicial
        self.editor.insert(
            "1.0",
            "class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hola mundo desde Java!\");\n"
            "    }\n"
            "}\n",
        )

        _set_theme(self.root, self.dark_mode.get())

    # =====================================================
    # Acciones GUI
    # =====================================================
    def _apply_theme(self):
        _set_theme(self.root, self.dark_mode.get())

    def _open_file(self):
        path = filedialog.askopenfilename(title="Abrir archivo Java", filetypes=[("Java files", "*.java")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
                return
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", code)

    def _save_output(self):
        out = self.output.get("1.0", "end-1c")
        if not out.strip():
            messagebox.showinfo("Guardar", "No hay salida para guardar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".java", filetypes=[("Java files", "*.java")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
                return
            messagebox.showinfo("Guardar", f"Guardado en {path}")

    def _compile(self):
        src = self.editor.get("1.0", "end-1c")
        mode = self.view_mode.get()
        res = _compile_pipeline(src, opt_level=self.opt_level.get(), mode=mode)

        # limpiar lista de diagnósticos
        self.diag_list.delete(0, "end")

        # preparar output
        self.output.config(state="normal")
        self.output.delete("1.0", "end")

        if mode == "default":
            self.output.insert("1.0", res["javaCode"])
        elif mode == "ast":
            try:
                self.output.insert("1.0", json.dumps(res["ast"], ensure_ascii=False, indent=2, default=str))
            except Exception:
                self.output.insert("1.0", str(res["ast"]))
        else:
            try:
                self.output.insert("1.0", json.dumps(res["ir"], ensure_ascii=False, indent=2, default=str))
            except Exception:
                self.output.insert("1.0", str(res["ir"]))

        # insertar errors y warnings en la lista (con color)
        for d in res["errors"]:
            text = f"[{d.get('stage','?')}] {d.get('message','')} (L{d.get('line',0)},C{d.get('col',0)})"
            self.diag_list.insert("end", text)
            # conseguir índice del último elemento y aplicar color
            idx = self.diag_list.size() - 1
            try:
                # itemconfig acepta 'foreground' en muchas plataformas; si falla, lo ignoramos.
                self.diag_list.itemconfig(idx, foreground="#d32f2f")
            except Exception:
                pass

        for d in res["warnings"]:
            text = f"[{d.get('stage','?')}] {d.get('message','')} (L{d.get('line',0)},C{d.get('col',0)})"
            self.diag_list.insert("end", text)
            idx = self.diag_list.size() - 1
            try:
                self.diag_list.itemconfig(idx, foreground="#f57c00")
            except Exception:
                pass

        # dejar output en modo readonly para evitar ediciones accidentales
        self.output.config(state="disabled")

    def _jump_to_diag(self, event=None):
        sel = self.diag_list.curselection()
        if not sel:
            return
        text = self.diag_list.get(sel[0])
        try:
            pos = text.split("(L", 1)[1].split(")")[0]
            line, col = map(int, pos.split(",C"))
            _highlight_line(self.editor, line)
            _text_goto(self.editor, line, col)
        except Exception:
            # no hacemos nada si no se puede parsear la posición
            pass

    # =====================================================
    # Nueva función: Ejecutar programa Java real
    # =====================================================
    def _run_java(self):
        src = self.editor.get("1.0", "end-1c")
        res = _compile_pipeline(src, opt_level=self.opt_level.get(), mode="default")

        if not res["ok"]:
            messagebox.showerror("Errores", "No se puede ejecutar: hay errores en el código.")
            return

        java_code = res["javaCode"]
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = os.path.join(tmpdir, "Main.java")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(java_code)

            # Compilar con javac
            try:
                proc_compile = subprocess.run(["javac", src_path], capture_output=True, text=True)
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontró 'javac'. Asegúrate de tener JDK instalado y 'javac' en el PATH.")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Error al ejecutar 'javac':\n{e}")
                return

            self.output.config(state="normal")
            self.output.delete("1.0", "end")

            if proc_compile.returncode != 0:
                self.output.insert("1.0", f"Errores de compilación:\n{proc_compile.stderr}")
                self.output.config(state="disabled")
                return

            # Ejecutar
            try:
                proc_run = subprocess.run(["java", "-cp", tmpdir, "Main"], capture_output=True, text=True)
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontró 'java'. Asegúrate de tener JRE/JDK instalado y 'java' en el PATH.")
                self.output.config(state="disabled")
                return
            except Exception as e:
                self.output.insert("1.0", f"Error al ejecutar 'java':\n{e}")
                self.output.config(state="disabled")
                return

            if proc_run.returncode == 0:
                out_text = proc_run.stdout or "(sin salida)"
                self.output.insert("1.0", f"Salida del programa:\n{out_text}")
            else:
                # mostrar stderr y stdout para diagnóstico
                stderr = proc_run.stderr or ""
                stdout = proc_run.stdout or ""
                self.output.insert("1.0", f"Error en ejecución:\n{stderr}\n{stdout}")

            self.output.config(state="disabled")

# ============================================================
# Punto de entrada
# ============================================================
def run_gui():
    root = tk.Tk()
    root.geometry("1200x700")
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
