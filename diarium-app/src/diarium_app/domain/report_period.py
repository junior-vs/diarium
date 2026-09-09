from datetime import date
from enum import Enum

class ReportMode(str, Enum):
    PERIODO = "periodo"
    TENDENCIA = "tendencia"

def classify_period(start: date, end: date, *, trend_threshold_days: int = 45) -> ReportMode:
    """Decide período vs. tendência (RF06/RF07). Pura, sem I/O — fácil de testar exaustivamente."""
    return ReportMode.TENDENCIA if (end - start).days > trend_threshold_days else ReportMode.PERIODO