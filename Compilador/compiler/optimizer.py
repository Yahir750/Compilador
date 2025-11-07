from __future__ import annotations
from dataclasses import replace
from typing import Tuple, List, Optional, Dict

from compiler.ir import (
    IRProgram, IRFunc, BasicBlock, Instr,
    LABEL, JUMP, CJUMP, MOVE, BINOP, CMP, CALL, RET
)
from compiler.diagnostics import Diagnostic

# -----------------------
# Utilidades de constantes
# -----------------------

def is_hash_const(x: str) -> bool:
    """Constantes numéricas inmediatas (formato '#<n>' o '#<float>')."""
    return isinstance(x, str) and x.startswith("#")

def parse_hash_const(x: str) -> Optional[float]:
    if not is_hash_const(x):
        return None
    try:
        # admite enteros o flotantes
        return float(x[1:])
    except ValueError:
        return None

def is_string_literal(x: str) -> bool:
    """Literales de cadena (incluye comillas)."""
    return isinstance(x, str) and len(x) >= 2 and x[0] == '"' and x[-1] == '"'

def to_hash(v: float) -> str:
    # Normaliza: si es entero exacto, sin .0
    if float(v).is_integer():
        return f"#{int(v)}"
    return f"#{v}"

# -----------------------
# Reglas algebraicas O1
# -----------------------

def simplify_binop(op: str, a: str, b: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Devuelve:
      - ("REPLACE_WITH_SRC", <reg/const>) -> usar esa fuente directamente (equivale a MOVE dst, src)
      - ("CONST", "#<n>") -> reemplazar por una constante
      - None -> no aplica
    """
    # reglas con identidad / anuladores
    if op == "ADD":
        # x + 0 -> x ; 0 + x -> x
        if is_hash_const(b) and parse_hash_const(b) == 0:
            return ("REPLACE_WITH_SRC", a)
        if is_hash_const(a) and parse_hash_const(a) == 0:
            return ("REPLACE_WITH_SRC", b)
    if op == "SUB":
        # x - 0 -> x
        if is_hash_const(b) and parse_hash_const(b) == 0:
            return ("REPLACE_WITH_SRC", a)
    if op == "MUL":
        # x * 1 -> x ; 1 * x -> x
        if is_hash_const(b) and parse_hash_const(b) == 1:
            return ("REPLACE_WITH_SRC", a)
        if is_hash_const(a) and parse_hash_const(a) == 1:
            return ("REPLACE_WITH_SRC", b)
        # x * 0 -> 0 ; 0 * x -> 0
        if (is_hash_const(a) and parse_hash_const(a) == 0) or (is_hash_const(b) and parse_hash_const(b) == 0):
            return ("CONST", "#0")
    if op == "DIV":
        # x / 1 -> x
        if is_hash_const(b) and parse_hash_const(b) == 1:
            return ("REPLACE_WITH_SRC", a)
        # 0 / x -> 0  (⚠️ sólo si x NO es 0 constante)
        if is_hash_const(a) and parse_hash_const(a) == 0 and not (is_hash_const(b) and parse_hash_const(b) == 0):
            return ("CONST", "#0")
    if op == "MOD":
        # x % 1 -> 0
        if is_hash_const(b) and parse_hash_const(b) == 1:
            return ("CONST", "#0")
    return None

def fold_binop(op: str, a: str, b: str) -> Optional[str]:
    """Si a y b son constantes, devuelve '#<resultado>' o None."""
    va = parse_hash_const(a)
    vb = parse_hash_const(b)
    if va is None or vb is None:
        return None
    try:
        if op == "ADD":  return to_hash(va + vb)
        if op == "SUB":  return to_hash(va - vb)
        if op == "MUL":  return to_hash(va * vb)
        if op == "DIV":
            if vb == 0:
                return None  # no fold división por cero
            return to_hash(va / vb)
        if op == "MOD":
            if vb == 0:
                return None
            # usar módulo de floats también (consistencia con parse)
            return to_hash(va % vb)
    except Exception:
        return None
    return None

def fold_cmp(a: str, op: str, b: str) -> Optional[str]:
    """Si a y b son constantes, devuelve '#1' o '#0'."""
    # soporta comparación entre numéricos; ignora strings (no v1)
    va = parse_hash_const(a)
    vb = parse_hash_const(b)
    if va is None or vb is None:
        return None
    if op == "==": return "#1" if va == vb else "#0"
    if op == "!=": return "#1" if va != vb else "#0"
    if op == "<":  return "#1" if va <  vb else "#0"
    if op == "<=": return "#1" if va <= vb else "#0"
    if op == ">":  return "#1" if va >  vb else "#0"
    if op == ">=": return "#1" if va >= vb else "#0"
    return None

# -----------------------
# Propagación local de constantes (por bloque)
# -----------------------

def propagate_block(instrs: List[Instr]) -> List[Instr]:
    """
    Reemplaza usos por constantes si hay información local en el bloque.
    Se invalida el mapeo al escribir en un destino con no-const.
    """
    const_map: Dict[str, str] = {}
    out: List[Instr] = []

    def subst(x: Optional[str]) -> Optional[str]:
        if x is None:
            return None
        if x in const_map:
            return const_map[x]
        return x

    for ins in instrs:
        if isinstance(ins, MOVE):
            src = subst(ins.src)
            dst = ins.dst
            # MOVE dst, dst -> elimina
            if src == dst:
                continue
            out.append(replace(ins, src=src))
            # registra constante si src es const inmediata o string literal
            if is_hash_const(src) or is_string_literal(src):
                const_map[dst] = src
            else:
                # invalida si ya estaba
                const_map.pop(dst, None)

        elif isinstance(ins, BINOP):
            a = subst(ins.a)
            b = subst(ins.b)
            out.append(replace(ins, a=a, b=b))
            # BINOP escribe dst => ya no es constante (salvo que pleguemos luego)
            const_map.pop(ins.dst, None)

        elif isinstance(ins, CMP):
            a = subst(ins.a)
            b = subst(ins.b)
            out.append(replace(ins, a=a, b=b))
            const_map.pop(ins.dst, None)

        elif isinstance(ins, CJUMP):
            cond = subst(ins.cond)
            out.append(replace(ins, cond=cond))

        elif isinstance(ins, CALL):
            # llamada: efectos desconocidos → conservador (no invalidamos todo, pero no marcamos nada)
            out.append(ins)

        else:
            out.append(ins)

    return out

# -----------------------
# Peephole por bloque
# -----------------------

def peephole_block(instrs: List[Instr], diags: List[Diagnostic]) -> List[Instr]:
    changed = True
    out = instrs
    # Iterar unas pocas veces para estabilizar
    for _ in range(3):
        if not changed:
            break
        changed = False
        new_list: List[Instr] = []
        for ins in out:
            if isinstance(ins, MOVE):
                # elimina MOVE x, x
                if ins.dst == ins.src:
                    changed = True
                    continue
                new_list.append(ins)

            elif isinstance(ins, BINOP):
                # reglas algebraicas simples
                simp = simplify_binop(ins.op, ins.a, ins.b)
                if simp is not None:
                    kind, val = simp
                    if kind == "REPLACE_WITH_SRC":
                        # reemplazar por MOVE dst, src
                        new_list.append(MOVE(dst=ins.dst, src=val, span=ins.span))
                        changed = True
                        continue
                    if kind == "CONST":
                        new_list.append(MOVE(dst=ins.dst, src=val, span=ins.span))
                        changed = True
                        continue

                # constant folding
                folded = fold_binop(ins.op, ins.a, ins.b)
                if folded is not None:
                    new_list.append(MOVE(dst=ins.dst, src=folded, span=ins.span))
                    changed = True
                    continue

                new_list.append(ins)

            elif isinstance(ins, CMP):
                folded = fold_cmp(ins.a, ins.op, ins.b)
                if folded is not None:
                    new_list.append(MOVE(dst=ins.dst, src=folded, span=ins.span))
                    changed = True
                    continue
                new_list.append(ins)

            elif isinstance(ins, CJUMP):
                # CJUMP true/false → JUMP directo o no-op
                c = ins.cond
                if is_hash_const(c):
                    vc = parse_hash_const(c)
                    if vc is not None:
                        if vc != 0:  # true
                            new_list.append(JUMP(target=ins.if_true, span=ins.span))
                        else:
                            new_list.append(JUMP(target=ins.if_false, span=ins.span))
                        changed = True
                        continue
                new_list.append(ins)

            else:
                new_list.append(ins)

        # pequeña pasada de propagación local (después de simplificar)
        new_list2 = propagate_block(new_list)
        if new_list2 != new_list:
            changed = True
        out = new_list2

    return out

# -----------------------
# Optimización de todo el programa
# -----------------------

def optimize(ir: IRProgram, level: int = 1) -> Tuple[IRProgram, List[Diagnostic]]:
    """
    level=0 -> sin cambios.
    level=1 -> algebra + folding + propagación local + simplificación CJUMP constante + eliminación MOVE x,x
    """
    if level <= 0:
        return ir, []

    diags: List[Diagnostic] = []
    new_funcs: List[IRFunc] = []

    for f in ir.funcs:
        new_blocks: List[BasicBlock] = []
        for b in f.blocks:
            instrs = list(b.instrs)
            # no tocar la primera LABEL
            head = []
            tail = instrs
            if instrs and isinstance(instrs[0], LABEL):
                head = [instrs[0]]
                tail = instrs[1:]

            tail_opt = peephole_block(tail, diags)

            new_blocks.append(BasicBlock(b.label, tuple(head + tail_opt)))
        new_funcs.append(IRFunc(f.name, f.params, tuple(new_blocks), f.temps))

    return IRProgram(tuple(new_funcs)), diags
