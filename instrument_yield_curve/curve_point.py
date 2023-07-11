from dataclasses import dataclass
from datetime import date

@dataclass
class CurvePoint:
    base_date: date
    spot_rate: float
