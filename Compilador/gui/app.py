from __future__ import annotations
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
import subprocess
import tempfile
import os
import re

# Importar componentes del compilador
from compiler import lexer, parser, semantics, ir, optimizer, codegen_java, diagnostics
from compiler.formatter_java import format_java

APP_TITLE = "Compilador Java → Java"

# ============================================================
# Helpers visuales
# ============================================================
def _text_goto(text: tk.Text, line: int, col: int) -> None:
    col_index = max(col - 1, 0)
    text.mark_set("insert", f"{line}.{col_index}")
    text.see(f"{line}.0")
    text.focus_set()

def _clear_tags(text: tk.Text) -> None:
    for tag in text.tag_names():
        if not tag.startswith("syntax_"):
            text.tag_remove(tag, "1.0", "end")

def _highlight_line(text: tk.Text, line: int, tag="highlight_line"):
    _clear_tags(text)
    text.tag_configure(tag, background="#fff3cd")
    text.tag_add(tag, f"{line}.0", f"{line}.0 lineend")

def _apply_syntax_highlighting(text: tk.Text, dark: bool):
    """Aplica syntax highlighting básico para Java"""
    # Limpiar tags de sintaxis previos
    for tag in text.tag_names():
        if tag.startswith("syntax_"):
            text.tag_remove(tag, "1.0", "end")
    
    # Colores según modo
    if dark:
        colors = {
            "keyword": "#569CD6",
            "string": "#CE9178",
            "comment": "#6A9955",
            "number": "#B5CEA8",
            "type": "#4EC9B0",
        }
    else:
        colors = {
            "keyword": "#0000FF",
            "string": "#A31515",
            "comment": "#008000",
            "number": "#098658",
            "type": "#267F99",
        }
    
    # Configurar tags
    text.tag_configure("syntax_keyword", foreground=colors["keyword"], font=("Consolas", 11, "bold"))
    text.tag_configure("syntax_string", foreground=colors["string"])
    text.tag_configure("syntax_comment", foreground=colors["comment"], font=("Consolas", 11, "italic"))
    text.tag_configure("syntax_number", foreground=colors["number"])
    text.tag_configure("syntax_type", foreground=colors["type"])
    
    content = text.get("1.0", "end-1c")
    
    # Comentarios
    for match in re.finditer(r'//[^\n]*', content):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_comment", start_idx, end_idx)
    
    for match in re.finditer(r'/\*.*?\*/', content, re.DOTALL):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_comment", start_idx, end_idx)
    
    # Strings
    for match in re.finditer(r'"(?:[^"\\]|\\.)*"', content):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_string", start_idx, end_idx)
    
    # Números
    for match in re.finditer(r'\b\d+\.?\d*\b', content):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_number", start_idx, end_idx)
    
    # Palabras clave
    keywords = r'\b(public|private|static|void|int|double|boolean|class|if|else|while|for|return|new|true|false|break|continue)\b'
    for match in re.finditer(keywords, content):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_keyword", start_idx, end_idx)
    
    # Tipos (String, System, etc)
    for match in re.finditer(r'\b[A-Z][a-zA-Z0-9_]*\b', content):
        start_idx = f"1.0+{match.start()}c"
        end_idx = f"1.0+{match.end()}c"
        text.tag_add("syntax_type", start_idx, end_idx)

def _set_theme(root: tk.Tk, dark: bool):
    bg = "#1e1e1e" if dark else "#ffffff"
    fg = "#d4d4d4" if dark else "#000000"
    panel_bg = "#252526" if dark else "#f3f3f3"
    button_bg = "#0e639c" if dark else "#007acc"
    
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=panel_bg)
    style.configure("TFrame", background=panel_bg)
    style.configure("TLabel", background=panel_bg, foreground=fg, font=("Segoe UI", 9))
    style.configure("TButton", 
                   background=button_bg,
                   foreground="#ffffff", 
                   relief="flat", 
                   padding=8,
                   font=("Segoe UI", 9))
    style.map("TButton", 
             background=[("active", "#1177bb"), ("pressed", "#0c5a9e")])
    
    style.configure("TRadiobutton", background=panel_bg, foreground=fg, font=("Segoe UI", 9))
    style.configure("TCheckbutton", background=panel_bg, foreground=fg, font=("Segoe UI", 9))
    
    for w in root.winfo_children():
        _apply_widget_colors(w, bg, fg, panel_bg)

def _apply_widget_colors(widget, bg, fg, panel_bg):
    try:
        if isinstance(widget, tk.Text):
            widget.configure(bg=bg, fg=fg, insertbackground=fg, highlightbackground=panel_bg)
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg="#fafafa", fg="#000000")
    except Exception:
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
        self.last_compile_time = 0
        self.last_error_count = 0
        self.last_warning_count = 0

        outer = ttk.Frame(root, padding=10)
        outer.pack(fill="both", expand=True)

        # ===== BARRA SUPERIOR =====
        toolbar = ttk.Frame(outer)
        toolbar.pack(fill="x", pady=(0, 8))

        # Grupo de archivos
        file_frame = ttk.Frame(toolbar)
        file_frame.pack(side="left", padx=5)
        ttk.Button(file_frame, text="Abrir", command=self._open_file, width=10).pack(side="left", padx=2)
        ttk.Button(file_frame, text="Guardar", command=self._save_output, width=10).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        # Grupo de compilación
        compile_frame = ttk.Frame(toolbar)
        compile_frame.pack(side="left", padx=5)
        ttk.Button(compile_frame, text="Compilar", command=self._compile, width=12).pack(side="left", padx=2)
        ttk.Button(compile_frame, text="Ejecutar", command=self._run_java, width=12).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        # Optimización
        opt_frame = ttk.Frame(toolbar)
        opt_frame.pack(side="left", padx=5)
        ttk.Label(opt_frame, text="Optimización:").pack(side="left", padx=3)
        ttk.Radiobutton(opt_frame, text="O0", variable=self.opt_level, value=0).pack(side="left", padx=2)
        ttk.Radiobutton(opt_frame, text="O1", variable=self.opt_level, value=1).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        # Vista
        view_frame = ttk.Frame(toolbar)
        view_frame.pack(side="left", padx=5)
        ttk.Label(view_frame, text="Vista:").pack(side="left", padx=3)
        ttk.Radiobutton(view_frame, text="Java", variable=self.view_mode, value="default", command=self._compile).pack(side="left", padx=2)
        ttk.Radiobutton(view_frame, text="AST", variable=self.view_mode, value="ast", command=self._compile).pack(side="left", padx=2)
        ttk.Radiobutton(view_frame, text="IR", variable=self.view_mode, value="ir", command=self._compile).pack(side="left", padx=2)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        # Modo oscuro
        ttk.Checkbutton(toolbar, text="Modo oscuro", variable=self.dark_mode, command=self._apply_theme).pack(side="left", padx=5)

        # ===== ÁREA CENTRAL - EDITOR Y SALIDA =====
        middle = ttk.Panedwindow(outer, orient="horizontal")
        middle.pack(fill="both", expand=True, pady=8)

        # Editor izquierdo con números de línea
        left_container = ttk.Frame(middle)
        
        editor_header = ttk.Frame(left_container)
        editor_header.pack(fill="x", pady=(0, 4))
        ttk.Label(editor_header, text="Código fuente", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        editor_frame = ttk.Frame(left_container)
        editor_frame.pack(fill="both", expand=True)
        
        # Números de línea
        self.line_numbers = tk.Text(editor_frame, width=4, padx=3, takefocus=0, border=0,
                                     background="#f0f0f0", state="disabled", wrap="none",
                                     font=("Consolas", 11))
        self.line_numbers.pack(side="left", fill="y")
        
        # Editor principal
        self.editor = tk.Text(editor_frame, wrap="none", undo=True, font=("Consolas", 11),
                             insertbackground="#000000", selectbackground="#ADD6FF")
        self.editor.pack(side="left", fill="both", expand=True)
        self.editor.bind("<KeyRelease>", self._on_editor_change)
        self.editor.bind("<MouseWheel>", self._on_scroll)
        
        # Scrollbar
        editor_scroll_y = ttk.Scrollbar(editor_frame, orient="vertical", command=self._on_scrollbar)
        editor_scroll_y.pack(side="right", fill="y")
        self.editor.configure(yscrollcommand=editor_scroll_y.set)
        
        middle.add(left_container, weight=1)

        # Panel derecho - salida
        right_container = ttk.Frame(middle)
        
        output_header = ttk.Frame(right_container)
        output_header.pack(fill="x", pady=(0, 4))
        ttk.Label(output_header, text="Salida compilada", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        self.output = tk.Text(right_container, wrap="none", state="disabled", font=("Consolas", 11),
                             selectbackground="#ADD6FF")
        self.output.pack(fill="both", expand=True)
        
        middle.add(right_container, weight=1)

        # ===== PANEL INFERIOR - DIAGNÓSTICOS =====
        bottom = ttk.Frame(outer)
        bottom.pack(fill="both", expand=False, pady=(8, 0))
        
        diag_header = ttk.Frame(bottom)
        diag_header.pack(fill="x", pady=(0, 4))
        ttk.Label(diag_header, text="Diagnosticos", font=("Segoe UI", 10, "bold")).pack(side="left")
        
        # Frame con tabs para errores/warnings
        self.diag_notebook = ttk.Notebook(bottom)
        self.diag_notebook.pack(fill="both", expand=False)
        
        # Tab de todos
        all_frame = ttk.Frame(self.diag_notebook)
        self.diag_list = tk.Listbox(all_frame, height=6, bg="#fafafa", font=("Consolas", 9),
                                    selectbackground="#0078d7", selectforeground="white")
        self.diag_list.pack(fill="both", expand=True)
        self.diag_list.bind("<<ListboxSelect>>", self._jump_to_diag)
        self.diag_notebook.add(all_frame, text="Todos")
        
        # Tab de errores
        errors_frame = ttk.Frame(self.diag_notebook)
        self.error_list = tk.Listbox(errors_frame, height=6, bg="#fafafa", font=("Consolas", 9),
                                     selectbackground="#0078d7", selectforeground="white")
        self.error_list.pack(fill="both", expand=True)
        self.error_list.bind("<<ListboxSelect>>", self._jump_to_error)
        self.diag_notebook.add(errors_frame, text="Errores (0)")
        
        # Tab de warnings
        warnings_frame = ttk.Frame(self.diag_notebook)
        self.warning_list = tk.Listbox(warnings_frame, height=6, bg="#fafafa", font=("Consolas", 9),
                                       selectbackground="#0078d7", selectforeground="white")
        self.warning_list.pack(fill="both", expand=True)
        self.warning_list.bind("<<ListboxSelect>>", self._jump_to_warning)
        self.diag_notebook.add(warnings_frame, text="Warnings (0)")

        # ===== BARRA DE ESTADO =====
        status_bar = ttk.Frame(outer)
        status_bar.pack(fill="x", pady=(4, 0))
        
        self.status_label = ttk.Label(status_bar, text="Listo", anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        self.stats_label = ttk.Label(status_bar, text="", anchor="e")
        self.stats_label.pack(side="right")

        # Ejemplo inicial
        self.editor.insert(
            "1.0",
            "class Main {\n"
            "    public static void main(String[] args) {\n"
            "        int a = 5;\n"
            "        double b = 2.5;\n"
            "        boolean ok = true;\n\n"
            "        if (ok && a > 3) {\n"
            "            System.out.println(\"Mayor que 3\");\n"
            "        }\n\n"
            "        for (int i = 0; i < 3; i = i + 1) {\n"
            "            System.out.println(i);\n"
            "        }\n\n"
            "        System.out.println(a + b);\n"
            "    }\n"
            "}\n",
        )

        self._update_line_numbers()
        _set_theme(self.root, self.dark_mode.get())
        self._apply_syntax_highlighting()

    # =====================================================
    # Métodos auxiliares
    # =====================================================
    def _update_line_numbers(self):
        """Actualiza los números de línea"""
        line_count = int(self.editor.index("end-1c").split(".")[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count))
        
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.config(state="disabled")
    
    def _on_editor_change(self, event=None):
        """Callback cuando cambia el editor"""
        self._update_line_numbers()
        # Aplicar syntax highlighting con delay para no afectar performance
        self.root.after(100, self._apply_syntax_highlighting)
    
    def _on_scroll(self, event=None):
        """Sincronizar scroll de números de línea"""
        self.line_numbers.yview_moveto(self.editor.yview()[0])
        return "break"
    
    def _on_scrollbar(self, *args):
        """Sincronizar scrollbar con editor y números"""
        self.editor.yview(*args)
        self.line_numbers.yview(*args)
    
    def _apply_syntax_highlighting(self):
        """Aplica syntax highlighting al editor"""
        _apply_syntax_highlighting(self.editor, self.dark_mode.get())
    
    def _update_status(self, message: str):
        """Actualiza la barra de estado"""
        self.status_label.config(text=message)
    
    def _update_stats(self):
        """Actualiza las estadísticas en la barra de estado"""
        stats = f"Tiempo: {self.last_compile_time}ms | Errores: {self.last_error_count} | Warnings: {self.last_warning_count}"
        self.stats_label.config(text=stats)

    # =====================================================
    # Acciones GUI
    # =====================================================
    def _apply_theme(self):
        _set_theme(self.root, self.dark_mode.get())
        self._apply_syntax_highlighting()
        
        # Actualizar colores de números de línea
        if self.dark_mode.get():
            self.line_numbers.config(background="#2d2d2d", foreground="#858585")
        else:
            self.line_numbers.config(background="#f0f0f0", foreground="#6e6e6e")

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Abrir archivo Java", 
            filetypes=[("Archivos Java", "*.java"), ("Todos los archivos", "*.*")]
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code = f.read()
                self.editor.delete("1.0", "end")
                self.editor.insert("1.0", code)
                self._update_line_numbers()
                self._apply_syntax_highlighting()
                self._update_status(f"Archivo cargado: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
                self._update_status("Error al cargar archivo")

    def _save_output(self):
        out = self.output.get("1.0", "end-1c")
        if not out.strip():
            messagebox.showinfo("Guardar", "No hay salida para guardar.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".java", 
            filetypes=[("Archivos Java", "*.java"), ("Todos los archivos", "*.*")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)
                messagebox.showinfo("Guardar", f"Guardado exitosamente")
                self._update_status(f"Archivo guardado: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
                self._update_status("Error al guardar archivo")

    def _compile(self):
        src = self.editor.get("1.0", "end-1c")
        mode = self.view_mode.get()
        
        self._update_status("Compilando...")
        self.root.update_idletasks()
        
        res = _compile_pipeline(src, opt_level=self.opt_level.get(), mode=mode)

        # Limpiar listas de diagnósticos
        self.diag_list.delete(0, "end")
        self.error_list.delete(0, "end")
        self.warning_list.delete(0, "end")
        
        # Actualizar salida
        self.output.config(state="normal")
        self.output.delete("1.0", "end")

        if mode == "default":
            self.output.insert("1.0", res["javaCode"])
        elif mode == "ast":
            self.output.insert("1.0", json.dumps(res["ast"], ensure_ascii=False, indent=2, default=str))
        else:
            self.output.insert("1.0", json.dumps(res["ir"], ensure_ascii=False, indent=2, default=str))

        # Procesar errores
        error_count = 0
        for d in res["errors"]:
            msg = f"[{d.get('stage', '?')}] {d.get('message')} (Línea {d.get('line')}, Col {d.get('col')})"
            self.diag_list.insert("end", msg)
            self.diag_list.itemconfig("end", foreground="#d32f2f")
            self.error_list.insert("end", msg)
            self.error_list.itemconfig("end", foreground="#d32f2f")
            error_count += 1

        # Procesar warnings
        warning_count = 0
        for d in res["warnings"]:
            msg = f"[{d.get('stage', '?')}] {d.get('message')} (Línea {d.get('line')}, Col {d.get('col')})"
            self.diag_list.insert("end", msg)
            self.diag_list.itemconfig("end", foreground="#f57c00")
            self.warning_list.insert("end", msg)
            self.warning_list.itemconfig("end", foreground="#f57c00")
            warning_count += 1

        # Actualizar tabs con contadores
        self.diag_notebook.tab(1, text=f"Errores ({error_count})")
        self.diag_notebook.tab(2, text=f"Warnings ({warning_count})")

        self.output.config(state="disabled")
        
        # Guardar estadísticas
        self.last_compile_time = res.get("logs", [])[-1] if res.get("logs") else 0
        self.last_error_count = error_count
        self.last_warning_count = warning_count
        
        # Actualizar estado
        if res["ok"]:
            self._update_status("Compilacion exitosa")
        else:
            self._update_status(f"Compilacion fallida ({error_count} errores)")
        
        self._update_stats()

    def _jump_to_diag(self, event=None):
        sel = self.diag_list.curselection()
        if not sel:
            return
        self._jump_to_diagnostic(self.diag_list.get(sel[0]))
    
    def _jump_to_error(self, event=None):
        sel = self.error_list.curselection()
        if not sel:
            return
        self._jump_to_diagnostic(self.error_list.get(sel[0]))
    
    def _jump_to_warning(self, event=None):
        sel = self.warning_list.curselection()
        if not sel:
            return
        self._jump_to_diagnostic(self.warning_list.get(sel[0]))
    
    def _jump_to_diagnostic(self, text: str):
        """Salta a la línea del diagnóstico"""
        try:
            # Formato: "[stage] message (Línea X, Col Y)"
            pos = text.split("(Línea ", 1)[1].split(")")[0]
            line_str, col_str = pos.split(", Col ")
            line = int(line_str)
            col = int(col_str)
            _highlight_line(self.editor, line)
            _text_goto(self.editor, line, col)
        except Exception:
            pass

    def _run_java(self):
        src = self.editor.get("1.0", "end-1c")
        
        self._update_status("Compilando para ejecutar...")
        self.root.update_idletasks()
        
        res = _compile_pipeline(src, opt_level=self.opt_level.get(), mode="default")

        if not res["ok"]:
            messagebox.showerror("Errores de compilacion", 
                               f"No se puede ejecutar: hay {len(res['errors'])} errores en el codigo.")
            self._update_status("No se puede ejecutar por errores")
            return

        java_code = res["javaCode"]

        with tempfile.TemporaryDirectory() as tmpdir:
            match = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", java_code)
            class_name = match.group(1) if match else "Main"
            src_path = os.path.join(tmpdir, f"{class_name}.java")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(java_code)

            # Compilar
            self._update_status("Compilando con javac...")
            self.root.update_idletasks()
            
            try:
                proc_compile = subprocess.run(["javac", src_path], capture_output=True, text=True, timeout=10)
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontro 'javac'.\n\nAsegurate de tener el JDK instalado y en el PATH.")
                self._update_status("javac no encontrado")
                return
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "La compilacion tardo demasiado (timeout).")
                self._update_status("Timeout en compilacion")
                return

            self.output.config(state="normal")
            self.output.delete("1.0", "end")

            if proc_compile.returncode != 0:
                self.output.insert("1.0", f"Errores de javac:\n\n{proc_compile.stderr}")
                self.output.config(state="disabled")
                self._update_status("Error en javac")
                return

            # Ejecutar
            self._update_status("Ejecutando programa...")
            self.root.update_idletasks()
            
            try:
                proc_run = subprocess.run(["java", "-cp", tmpdir, class_name], 
                                         capture_output=True, text=True, timeout=10)
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontro 'java'.\n\nAsegurate de tener el JRE/JDK instalado y en el PATH.")
                self._update_status("java no encontrado")
                return
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "La ejecucion tardo demasiado (timeout).")
                self._update_status("Timeout en ejecucion")
                return

            if proc_run.returncode == 0:
                out_text = proc_run.stdout.strip() or "(sin salida)"
                self.output.insert("1.0", f"Salida del programa:\n\n{out_text}\n")
                self._update_status("Ejecucion exitosa")
            else:
                err_text = proc_run.stderr.strip()
                self.output.insert("1.0", f"Error en ejecucion (codigo {proc_run.returncode}):\n\n{err_text}\n")
                self._update_status(f"Error en ejecucion (codigo {proc_run.returncode})")

            self.output.config(state="disabled")

# ============================================================
# Punto de entrada
# ============================================================
def run_gui():
    root = tk.Tk()
    root.geometry("1400x800")
    root.minsize(1000, 600)
    
    # Intentar usar el ícono de Python si está disponible
    try:
        root.iconbitmap(default="")
    except:
        pass
    
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
