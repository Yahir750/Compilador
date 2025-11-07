from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, List, Dict, Tuple

Severity = Literal["error","warning","info"]

@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    stage: str
    message: str
    line: int
    col: int
    end_line: int
    end_col: int
    code: str
    notes: Tuple[str, ...] = ()

def to_json(diags: List[Diagnostic]) -> List[Dict]:
    """Convierte una lista de Diagnostic a lista de dicts serializables en JSON."""
    return [dict(
        severity=d.severity,
        stage=d.stage,
        message=d.message,
        line=d.line,
        col=d.col,
        end_line=d.end_line,
        end_col=d.end_col,
        code=d.code,
        notes=list(d.notes)
    ) for d in diags]
