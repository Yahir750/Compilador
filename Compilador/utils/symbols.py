from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from compiler.ast_nodes import TypeRef, Span

@dataclass(frozen=True)
class Symbol:
    name: str
    type: TypeRef
    span: Span
    kind: str  # "var" | "param" | "method" | "class"

class SymbolTable:
    """
    Tabla de símbolos con ámbitos anidados (pila de diccionarios).
    Además, rastrea uso de variables para warnings de 'no usadas'.
    """
    def __init__(self):
        self._scopes: List[Dict[str, Symbol]] = [ {} ]
        # Pila paralela para uso de símbolos (solo var/param)
        self._usage_stack: List[Dict[str, bool]] = [ {} ]

    # ---------------- Ámbitos ----------------
    def enter(self) -> None:
        self._scopes.append({})
        self._usage_stack.append({})

    def exit(self) -> Tuple[Dict[str, Symbol], Dict[str, bool]]:
        scope = self._scopes.pop()
        usage = self._usage_stack.pop()
        return scope, usage

    # ---------------- Definir/Resolver ----------------
    def define(self, sym: Symbol) -> bool:
        """Devuelve False si ya existía en el ámbito actual (colisión); True si se define."""
        cur = self._scopes[-1]
        if sym.name in cur:
            return False
        cur[sym.name] = sym
        # sólo marcamos uso para variables/parámetros
        if sym.kind in ("var","param"):
            self._usage_stack[-1][sym.name] = False
        return True

    def resolve(self, name: str) -> Optional[Symbol]:
        """Busca desde el ámbito más interno hacia fuera."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def resolve_in_current(self, name: str) -> Optional[Symbol]:
        return self._scopes[-1].get(name)

    # ---------------- Uso ----------------
    def mark_used(self, name: str) -> None:
        # Marca en el primer ámbito donde exista la variable/param
        for usage, scope in zip(reversed(self._usage_stack), reversed(self._scopes)):
            if name in scope and (scope[name].kind in ("var","param")) and (name in usage):
                usage[name] = True
                return

    def unused_in_current(self) -> List[str]:
        """Devuelve variables/parámetros no usados del ámbito actual."""
        usage = self._usage_stack[-1]
        return [name for name, used in usage.items() if not used]
