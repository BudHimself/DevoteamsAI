from pydantic import BaseModel, Field

from devoteam_test.models.anomaly import Severity


class NumericThresholdRule(BaseModel):
    max: float = Field(
        description="Seuil supérieur : anomalie si la métrique est strictement supérieure à max."
    )
    severity: Severity


class ServicesThresholdConfig(BaseModel):
    status_severity: dict[str, Severity] = Field(
        description="Statuts de service considérés comme anomalie et leur criticité.",
    )


class ThresholdConfig(BaseModel):
    version: int
    numeric: dict[str, NumericThresholdRule]
    services: ServicesThresholdConfig
