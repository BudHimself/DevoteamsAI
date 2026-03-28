import json
import logging
import os
import re
from typing import Any, Literal, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError

from devoteam_test.models.anomaly import Anomaly
from devoteam_test.models.snapshot import MetricSnapshot
from devoteam_test.state import GraphState
from devoteam_test.thresholds_schema import ThresholdConfig

logger = logging.getLogger(__name__)


def route_after_detect(state: GraphState) -> Literal["llm", "rules"]:
    if len(state.anomalies) > 1:
        return "llm"
    return "rules"


def _rule_messages(snapshot: MetricSnapshot, anomalies: list[Anomaly]) -> list[str]:
    if not anomalies:
        return [
            "Aucune anomalie détectée pour cette mesure selon les seuils configurés.",
        ]
    messages: list[str] = []
    for an in anomalies:
        if an.field and an.field.startswith("service_status"):
            messages.append(
                f"Prioriser l'investigation du service : {an.message}. "
                "Vérifier logs, dépendances et bascule éventuelle.",
            )
        elif an.field:
            messages.append(
                f"Analyser la métrique « {an.field} » : {an.message}. "
                "Envisager scale horizontal/vertical ou optimisation applicative.",
            )
        else:
            messages.append(an.message)
    return messages


def _build_summary(
    snapshot: MetricSnapshot,
    anomalies: list[Anomaly],
    source: Literal["rules", "none"],
) -> str:
    n = len(anomalies)
    if n == 0:
        return f"{snapshot.timestamp} — état nominal (0 anomalie)."
    return f"{snapshot.timestamp} — {n} anomalie(s) ; recommandations déterministes ({source})."


def make_rules_node(_thresholds: ThresholdConfig):
    def rules_node(state: GraphState) -> dict[str, object]:
        snap = MetricSnapshot.model_validate(state.snapshot)
        anoms = [Anomaly.model_validate(a) for a in state.anomalies]
        recs = _rule_messages(snap, anoms)
        src: Literal["rules", "none"] = "none" if not anoms else "rules"
        summary = _build_summary(snap, anoms, src)
        return {
            "recommendations": recs,
            "summary": summary,
            "recommendation_source": src,
        }

    return rules_node


class LlmRecommendationPayload(BaseModel):
    summary: str = Field(description="Résumé global de l'état et des actions.")
    recommendations: list[str] = Field(
        description="Actions concrètes, triées par priorité décroissante.",
    )


def _parse_llm_json_content(content: str) -> LlmRecommendationPayload | None:
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    decoder = json.JSONDecoder()
    for start_char in ("{", "["):
        pos = text.find(start_char)
        if pos < 0:
            continue
        try:
            obj, _ = decoder.raw_decode(text[pos:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            try:
                return LlmRecommendationPayload.model_validate(obj)
            except ValidationError:
                continue
        if isinstance(obj, list) and obj:
            first = obj[0]
            if isinstance(first, dict):
                try:
                    return LlmRecommendationPayload.model_validate(first)
                except ValidationError:
                    continue
    return None


def _fallback_to_rules(state: GraphState) -> dict[str, object]:
    snap = MetricSnapshot.model_validate(state.snapshot)
    anoms = [Anomaly.model_validate(a) for a in state.anomalies]
    recs = _rule_messages(snap, anoms)
    summary = _build_summary(snap, anoms, "rules")
    return {
        "recommendations": recs,
        "summary": summary + " (repli : LLM indisponible ou erreur d'appel).",
        "recommendation_source": "rules",
    }


def make_llm_node(thresholds: ThresholdConfig):
    def llm_node(state: GraphState) -> dict[str, object]:
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            logger.debug("OPENROUTER_API_KEY absent — repli sur les règles déterministes.")
            return _fallback_to_rules(state)

        snap = MetricSnapshot.model_validate(state.snapshot)
        anoms = [Anomaly.model_validate(a) for a in state.anomalies]

        model_name = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        llm = cast(Any, ChatOpenAI)(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
        )
        payload = json.dumps(
            {
                "metrics": snap.model_dump(mode="json"),
                "anomalies": [a.model_dump(mode="json") for a in anoms],
                "thresholds_version": thresholds.version,
            },
            ensure_ascii=False,
        )
        messages = [
            SystemMessage(
                content=(
                    "Tu es un ingénieur SRE. Réponds uniquement avec un objet JSON "
                    "valide (pas de markdown, pas de texte hors JSON). "
                    'Clés obligatoires : "summary" (string), "recommendations" '
                    "(array de strings, actions priorisées). "
                    "Exemple : "
                    '{"summary":"...","recommendations":["action 1","action 2"]}'
                ),
            ),
            HumanMessage(content=payload),
        ]
        try:
            ai = llm.invoke(messages)
            raw = ai.content
            if not isinstance(raw, str):
                raw = str(raw)
            out = _parse_llm_json_content(raw)
            if out is None:
                logger.warning(
                    "Réponse LLM non JSON exploitable (OpenRouter) — repli sur les règles.",
                )
                return _fallback_to_rules(state)
            return {
                "recommendations": out.recommendations,
                "summary": out.summary,
                "recommendation_source": "llm",
            }
        except Exception:
            logger.exception("Échec de l'appel LLM — repli sur les règles.")
            return _fallback_to_rules(state)

    return llm_node
