from pathlib import Path

import yaml
from pydantic import ValidationError

from devoteam_test.thresholds_schema import ThresholdConfig


def load_thresholds(path: Path) -> ThresholdConfig:
    try:
        raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        msg = f"Impossible de lire le fichier de seuils : {path}"
        raise RuntimeError(msg) from exc
    if raw is None or not isinstance(raw, dict):
        msg = f"Configuration YAML invalide ou vide : {path}"
        raise ValueError(msg)
    try:
        return ThresholdConfig.model_validate(raw)
    except ValidationError as exc:
        msg = f"Validation des seuils échouée pour {path}"
        raise ValueError(msg) from exc
