"""Local agent registry for the CrisisGrid orchestration control plane."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re
from typing import Any, Callable

from pydantic import BaseModel

from app.core.config import settings
from app.models.incident import Incident
from app.schemas.agents import AgentExecutionResult, AgentInput
from app.schemas.common import IncidentStatus
from app.services.alert_service import alert_service
from app.services.clustering_service import ClusteringService
from app.services.dispatch_service import dispatch_service
from app.services.verification_service import VerificationService
from app.services.watsonx_service import watsonx_service
from app.utils.time import utc_now


AgentHandler = Callable[[dict[str, Any]], AgentExecutionResult]


@dataclass(frozen=True)
class AgentRegistryEntry:
    """Registered local agent metadata and executable handler."""

    name: str
    version: str
    handler: AgentHandler
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]


PROMPT_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bignore (all )?(previous|prior|above) instructions\b",
        r"\boverride (the )?(system|developer|safety) instructions\b",
        r"\breveal (your )?(prompt|system prompt|secrets?|api keys?|tokens?)\b",
        r"\bshow (me )?(the )?(.env|environment variables|api keys?|tokens?)\b",
        r"\bact as (an )?(admin|root|system)\b",
        r"\bcall (a )?(tool|function|api) to\b",
    ]
]


def get_agent_registry() -> dict[str, AgentRegistryEntry]:
    """Return all local agents keyed by registry name."""

    return {
        entry.name: entry
        for entry in [
            AgentRegistryEntry(
                name="intake_agent",
                version="1.0",
                handler=intake_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="deduplication_agent",
                version="1.0",
                handler=deduplication_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="verification_agent",
                version="1.0",
                handler=verification_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="clustering_agent",
                version="1.0",
                handler=clustering_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="priority_agent",
                version="1.0",
                handler=priority_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="alert_agent",
                version="1.0",
                handler=alert_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
            AgentRegistryEntry(
                name="dispatch_agent",
                version="1.0",
                handler=dispatch_agent,
                input_schema=AgentInput,
                output_schema=AgentExecutionResult,
            ),
        ]
    }


def _result(
    agent_name: str,
    status: str,
    started_at,
    output: dict[str, Any] | None = None,
    confidence: float = 0.0,
    errors: list[str] | None = None,
) -> AgentExecutionResult:
    completed_at = utc_now()
    normalized_confidence = max(0.0, min(1.0, confidence))
    return AgentExecutionResult(
        agent_name=agent_name,
        status=status,
        output=output or {},
        confidence=normalized_confidence,
        errors=errors or [],
        started_at=started_at,
        completed_at=completed_at,
    )


def _field(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)


def _enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def _sanitize_text(value: Any, max_length: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return escape(text[:max_length], quote=False)


def _detect_prompt_injection(*values: Any) -> bool:
    text = " ".join(str(value or "") for value in values)
    return any(pattern.search(text) for pattern in PROMPT_INJECTION_PATTERNS)


def _context_report(context: dict[str, Any]) -> Any:
    return context.get("report") or context.get("raw_report") or context


def intake_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    report = _context_report(context)
    description = _sanitize_text(_field(report, "description", ""), 1000) or ""
    location_text = _sanitize_text(_field(report, "location_text"), 255)
    image_url = _sanitize_text(_field(report, "image_url"), 2048)
    video_url = _sanitize_text(_field(report, "video_url"), 2048)
    prompt_injection_detected = _detect_prompt_injection(description, location_text)

    output = {
        "report_id": str(_field(report, "id", _field(report, "report_id", ""))),
        "crisis_type": _enum_value(_field(report, "crisis_type", "OTHER")),
        "description": description,
        "latitude": float(_field(report, "latitude", 0.0)),
        "longitude": float(_field(report, "longitude", 0.0)),
        "location_text": location_text,
        "image_url": image_url,
        "video_url": video_url,
        "is_anonymous": bool(_field(report, "is_anonymous", False)),
        "prompt_injection_detected": prompt_injection_detected,
        "admin_review_required": prompt_injection_detected,
    }
    confidence = 0.4 if prompt_injection_detected else 1.0
    return _result("intake_agent", "SUCCESS", started_at, output, confidence)


def deduplication_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    report = context.get("report")
    db = context.get("db")
    matched_incident_id = context.get("matched_incident_id")

    if db is not None and report is not None:
        matched_incident = ClusteringService(db).find_matching_incident(report)
        matched_incident_id = getattr(matched_incident, "id", None)

    output = {
        "match_existing": bool(matched_incident_id),
        "matched_incident_id": matched_incident_id,
    }
    return _result("deduplication_agent", "SUCCESS", started_at, output, 0.8)


def verification_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    db = context.get("db")
    report = context.get("report")

    if db is not None and report is not None:
        try:
            verification = VerificationService(db).verify_report(report.id)
            db.refresh(report)
            confidence = verification.final_confidence_score / 100.0
            output = {
                "verification_result": verification.verification_result.model_dump(mode="json"),
                "confidence": confidence,
                "severity_score": verification.final_severity_score,
                "decision": "VERIFIED" if verification.verified else "REVIEW",
                "report_status": verification.status.value,
                "agent_run_id": verification.agent_run_id,
                "admin_review_required": (
                    not verification.verified
                    or context.get("admin_review_required", False)
                ),
            }
            return _result("verification_agent", "SUCCESS", started_at, output, confidence)
        except ValueError as exc:
            if "already verified" not in str(exc).lower():
                raise
            confidence = float(getattr(report, "confidence_score", 0.0) or 0.0) / 100.0
            severity_score = float(getattr(report, "severity_score", 0.0) or 0.0)
            output = {
                "confidence": confidence,
                "severity_score": severity_score,
                "decision": "VERIFIED",
                "report_status": _enum_value(getattr(report, "status", None)),
                "admin_review_required": context.get("admin_review_required", False),
            }
            return _result("verification_agent", "SUCCESS", started_at, output, confidence)

    report_data = {
        "crisis_type": context.get("crisis_type", "OTHER"),
        "description": context.get("description", ""),
        "latitude": context.get("latitude"),
        "longitude": context.get("longitude"),
        "location_text": context.get("location_text"),
        "image_url": context.get("image_url"),
        "video_url": context.get("video_url"),
        "is_anonymous": context.get("is_anonymous", False),
    }
    analysis = watsonx_service.analyze_report(report_data)
    confidence = float(analysis.get("credibility_score", 0.0)) / 100.0
    decision = "VERIFIED" if confidence >= settings.AGENT_CONFIDENCE_THRESHOLD else "REVIEW"
    output = {
        "verification_result": analysis,
        "confidence": confidence,
        "severity_score": float(analysis.get("severity_score", 0.0)),
        "decision": decision,
        "admin_review_required": decision != "VERIFIED" or context.get("admin_review_required", False),
    }
    return _result("verification_agent", "SUCCESS", started_at, output, confidence)


def clustering_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    db = context.get("db")
    report = context.get("report")
    incident_id = context.get("matched_incident_id") or context.get("incident_id")
    incident_confidence = None

    if db is not None and report is not None:
        service = ClusteringService(db)
        matched_incident = service.find_matching_incident(report)
        if matched_incident is not None:
            incident = service.add_report_to_incident(report, matched_incident)
        else:
            result = service.cluster_reports(crisis_type=getattr(report, "crisis_type", None), min_reports=1)
            incident_ids = result.get("incident_ids") or []
            incident = None
            incident_id = incident_ids[0] if incident_ids else incident_id
        if matched_incident is not None:
            incident_id = getattr(incident, "id", incident_id)
        incident_confidence = _promote_incident_from_context(
            db=db,
            incident_id=incident_id,
            context=context,
            report=report,
        )

    output = {
        "incident_id": incident_id,
        "clustered": bool(incident_id),
        "incident_confidence": incident_confidence,
    }
    return _result("clustering_agent", "SUCCESS", started_at, output, context.get("confidence", 0.0))


def priority_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    confidence = float(context.get("confidence", 0.0))
    severity_score = float(context.get("severity_score", 0.0))

    if confidence >= 0.85 or severity_score >= 85:
        priority = "P1"
    elif confidence >= 0.7 or severity_score >= 70:
        priority = "P2"
    elif confidence >= 0.5 or severity_score >= 50:
        priority = "P3"
    else:
        priority = "P4"

    output = {
        "priority": priority,
        "confidence": confidence,
        "severity_score": severity_score,
        "admin_review_required": context.get("admin_review_required", False) or confidence < 0.6,
    }
    return _result("priority_agent", "SUCCESS", started_at, output, confidence)


def alert_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    db = context.get("db")
    incident_id = context.get("incident_id")
    alert_id = None

    if db is not None and incident_id:
        alert = alert_service.generate_alert(db, incident_id)
        alert_id = getattr(alert, "alert_id", None) if alert is not None else None

    output = {
        "alert_generated": bool(alert_id) or context.get("priority") in ["P1", "P2"],
        "alert_id": alert_id,
        "priority": context.get("priority"),
    }
    return _result("alert_agent", "SUCCESS", started_at, output, context.get("confidence", 0.0))


def dispatch_agent(context: dict[str, Any]) -> AgentExecutionResult:
    started_at = utc_now()
    db = context.get("db")
    incident_id = context.get("incident_id")
    alert_id = context.get("alert_id")
    dispatch_ids: list[str] = []

    if db is not None and incident_id:
        dispatches = dispatch_service.dispatch_authority(db, incident_id, alert_id=alert_id)
        dispatch_ids = [dispatch.dispatch_id for dispatch in dispatches]

    output = {
        "dispatch_created": bool(dispatch_ids),
        "dispatch_ids": dispatch_ids,
        "priority": context.get("priority"),
    }
    return _result("dispatch_agent", "SUCCESS", started_at, output, context.get("confidence", 0.0))


def _promote_incident_from_context(
    db,
    incident_id: str | None,
    context: dict[str, Any],
    report,
) -> float | None:
    if not incident_id:
        return None

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        return None

    confidence = float(context.get("confidence", 0.0) or 0.0) * 100
    severity_score = float(context.get("severity_score", confidence) or confidence)
    verified = context.get("decision") == "VERIFIED" and confidence >= (
        settings.AGENT_CONFIDENCE_THRESHOLD * 100
    )

    incident.media_confidence = max(float(incident.media_confidence or 0.0), confidence)
    incident.cross_report_confidence = max(
        float(incident.cross_report_confidence or 0.0),
        confidence,
    )
    incident.external_signal_confidence = max(
        float(incident.external_signal_confidence or 0.0),
        severity_score,
    )
    incident.reporter_trust_confidence = max(
        float(incident.reporter_trust_confidence or 0.0),
        50.0 if getattr(report, "is_anonymous", False) else 70.0,
    )
    incident.geo_time_consistency = max(float(incident.geo_time_consistency or 0.0), 80.0)

    if verified:
        incident.status = IncidentStatus.VERIFIED
    elif incident.status != IncidentStatus.VERIFIED:
        incident.status = IncidentStatus.NEEDS_CONFIRMATION

    incident.update_confidence_score()
    db.commit()
    db.refresh(incident)
    return float(incident.confidence_score or 0.0)
