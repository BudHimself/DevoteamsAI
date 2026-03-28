from typing import Literal

from pydantic import BaseModel

Severity = Literal["low", "medium", "high"]


class Anomaly(BaseModel):
    code: str
    message: str
    severity: Severity
    field: str | None = None
