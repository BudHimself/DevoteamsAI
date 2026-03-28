from typing import Any

from pydantic import BaseModel, Field


class GraphState(BaseModel):
    """État partagé entre les nœuds ; les mises à jour fusionnent champ par champ."""

    model_config = {"extra": "ignore"}

    snapshot: dict[str, Any] = Field(default_factory=dict)
    anomalies: list[dict[str, Any]] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    summary: str = ""
    recommendation_source: str = "none"
    line_report: dict[str, Any] | None = None
