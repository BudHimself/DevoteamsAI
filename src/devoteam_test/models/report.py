from pydantic import BaseModel

from devoteam_test.models.anomaly import Anomaly


class LineReport(BaseModel):
    timestamp: str
    anomalies: list[Anomaly]
    recommendations: list[str]
    summary: str
    recommendation_source: str


class AggregatedPipelineOutput(BaseModel):
    rows_analyzed: int
    reports: list[LineReport]
    global_summary: str
