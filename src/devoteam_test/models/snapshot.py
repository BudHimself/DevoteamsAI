from pydantic import BaseModel, Field


class MetricSnapshot(BaseModel):
    timestamp: str
    cpu_usage: int = Field(ge=0, le=100)
    memory_usage: int = Field(ge=0, le=100)
    latency_ms: int = Field(ge=0)
    disk_usage: int = Field(ge=0, le=100)
    network_in_kbps: int = Field(ge=0)
    network_out_kbps: int = Field(ge=0)
    io_wait: int = Field(ge=0, le=100)
    thread_count: int = Field(ge=0)
    active_connections: int = Field(ge=0)
    error_rate: float = Field(ge=0.0)
    uptime_seconds: int = Field(ge=0)
    temperature_celsius: int
    power_consumption_watts: int = Field(ge=0)
    service_status: dict[str, str]
