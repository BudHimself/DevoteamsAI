from devoteam_test.models.anomaly import Anomaly
from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.thresholds_schema import ThresholdConfig


def detect_anomalies(snapshot: MetricSnapshot, thresholds: ThresholdConfig) -> list[Anomaly]:
    anomalies: list[Anomaly] = []
    data = snapshot.model_dump()

    for field_name, rule in thresholds.numeric.items():
        if field_name not in data:
            continue
        value = data[field_name]
        if not isinstance(value, (int, float)):
            continue
        if float(value) > rule.max:
            anomalies.append(
                Anomaly(
                    code=f"numeric_{field_name}_above_max",
                    message=(
                        f"{field_name}={value} dépasse le seuil max={rule.max} "
                        f"(défini dans la configuration)"
                    ),
                    severity=rule.severity,
                    field=field_name,
                )
            )

    status_map = thresholds.services.status_severity
    for service_name, status in snapshot.service_status.items():
        if status in status_map:
            anomalies.append(
                Anomaly(
                    code=f"service_{status}",
                    message=f"Service « {service_name} » en état « {status} »",
                    severity=status_map[status],
                    field=f"service_status.{service_name}",
                )
            )

    return anomalies
