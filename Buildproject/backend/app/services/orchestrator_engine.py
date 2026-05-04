"""Local orchestration engine for CrisisGrid AI agent execution."""

from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import date, datetime
import logging
from pathlib import Path
import re
import time
from typing import Any

import yaml
from pydantic import ValidationError

from app.core.agent_registry import AgentRegistryEntry, get_agent_registry
from app.core.config import settings
from app.schemas.agents import (
    AgentExecutionResult,
    PipelineConfig,
    PipelineExecutionTrace,
    PipelineStepTrace,
)
from app.utils.time import utc_now


logger = logging.getLogger(__name__)


SECRET_KEY_PATTERN = re.compile(
    r"(api[_-]?key|token|secret|password|authorization|bearer|jwt|credential)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(bearer\s+)[a-z0-9._\-]+|"
    r"\beyJ[a-zA-Z0-9._\-]{20,}\b"
)


class OrchestratorEngineError(RuntimeError):
    """Raised when the local orchestration engine cannot run safely."""


class RateLimitExceeded(OrchestratorEngineError):
    """Raised when an agent exceeds its local in-process rate limit."""


class OrchestratorEngine:
    """Load and execute a local sequential agent pipeline."""

    def __init__(
        self,
        pipeline_path: str | Path | None = None,
        registry: dict[str, AgentRegistryEntry] | None = None,
        max_retries: int | None = None,
        timeout_seconds: float | None = None,
        enable_rate_limit: bool | None = None,
        rate_limit_per_minute: int | None = None,
    ) -> None:
        self.pipeline_path = self._resolve_pipeline_path(
            pipeline_path or settings.ORCHESTRATE_PIPELINE_CONFIG
        )
        self.registry = registry or get_agent_registry()
        self.max_retries = settings.AGENT_MAX_RETRIES if max_retries is None else max_retries
        self.timeout_seconds = (
            settings.AGENT_TIMEOUT_SECONDS if timeout_seconds is None else timeout_seconds
        )
        self.enable_rate_limit = (
            settings.ENABLE_AGENT_RATE_LIMIT
            if enable_rate_limit is None
            else enable_rate_limit
        )
        self.rate_limit_per_minute = (
            settings.AGENT_RATE_LIMIT_PER_MINUTE
            if rate_limit_per_minute is None
            else rate_limit_per_minute
        )
        self._rate_limit_window: dict[str, list[float]] = {}
        self.pipeline = self.load_pipeline()

    def load_pipeline(self) -> PipelineConfig:
        """Load and validate the configured local pipeline."""

        try:
            with self.pipeline_path.open("r", encoding="utf-8") as pipeline_file:
                payload = yaml.safe_load(pipeline_file) or {}
        except OSError as exc:
            raise OrchestratorEngineError(
                f"Pipeline config could not be read: {self.pipeline_path}"
            ) from exc

        try:
            pipeline = PipelineConfig.model_validate(payload)
        except ValidationError as exc:
            raise OrchestratorEngineError("Pipeline config failed validation") from exc

        unknown_agents = [
            step.name for step in pipeline.agents if step.name not in self.registry
        ]
        if unknown_agents:
            raise OrchestratorEngineError(
                f"Pipeline references unregistered agents: {', '.join(unknown_agents)}"
            )

        return pipeline

    def run(self, initial_context: dict[str, Any] | None = None) -> PipelineExecutionTrace:
        """Execute all configured agents and return a full trace."""

        started_at = utc_now()
        context: dict[str, Any] = dict(initial_context or {})
        steps: list[PipelineStepTrace] = []
        errors: list[str] = []

        logger.info("Pipeline started: %s", self.pipeline.pipeline_id)

        for step in self.pipeline.agents:
            step_started_at = utc_now()

            if step.condition and not self.evaluate_condition(step.condition, context):
                skipped_result = AgentExecutionResult(
                    agent_name=step.name,
                    status="SKIPPED",
                    output={"reason": "condition_not_met"},
                    confidence=float(context.get("confidence", 0.0) or 0.0),
                    errors=[],
                    started_at=step_started_at,
                    completed_at=utc_now(),
                )
                steps.append(
                    PipelineStepTrace(
                        agent_name=step.name,
                        status="SKIPPED",
                        condition=step.condition,
                        attempts=0,
                        result=skipped_result,
                        errors=[],
                        started_at=step_started_at,
                        completed_at=skipped_result.completed_at,
                    )
                )
                logger.info("Agent skipped: %s", step.name)
                continue

            result, attempts, step_errors = self._execute_with_retries(step.name, context)
            if result.status == "SUCCESS":
                self._merge_agent_output(context, result)
            else:
                errors.extend(step_errors)

            completed_at = utc_now()
            steps.append(
                PipelineStepTrace(
                    agent_name=step.name,
                    status=result.status,
                    condition=step.condition,
                    attempts=attempts,
                    result=result,
                    errors=step_errors,
                    started_at=step_started_at,
                    completed_at=completed_at,
                )
            )

        completed_at = utc_now()
        if errors:
            status = "PARTIAL" if any(step.status == "SUCCESS" for step in steps) else "FAILED"
        else:
            status = "SUCCESS"

        trace = PipelineExecutionTrace(
            pipeline_id=self.pipeline.pipeline_id,
            version=self.pipeline.version,
            mode=self.pipeline.mode,
            status=status,
            context=mask_sensitive(make_trace_safe(context)),
            steps=steps,
            errors=errors,
            started_at=started_at,
            completed_at=completed_at,
        )
        logger.info("Pipeline completed: %s status=%s", self.pipeline.pipeline_id, status)
        return trace

    def evaluate_condition(self, expression: str, context: dict[str, Any]) -> bool:
        """Evaluate a small allowlisted condition expression against context."""

        try:
            tree = ast.parse(expression, mode="eval")
            return bool(self._eval_condition_node(tree.body, context))
        except Exception as exc:
            logger.warning("Condition evaluation failed for expression: %s", expression)
            raise OrchestratorEngineError(
                f"Invalid pipeline condition: {mask_sensitive(str(exc))}"
            ) from exc

    def _execute_with_retries(
        self,
        agent_name: str,
        context: dict[str, Any],
    ) -> tuple[AgentExecutionResult, int, list[str]]:
        entry = self.registry[agent_name]
        attempts_allowed = max(1, self.max_retries + 1)
        errors: list[str] = []

        for attempt in range(1, attempts_allowed + 1):
            try:
                self._check_rate_limit(agent_name)
                logger.info("Agent execution started: %s attempt=%s", agent_name, attempt)
                result = self._run_with_timeout(entry, context)
                validated_result = entry.output_schema.model_validate(result)
                if validated_result.status == "SUCCESS":
                    logger.info(
                        "Agent execution completed: %s confidence=%.3f",
                        agent_name,
                        validated_result.confidence,
                    )
                    return validated_result, attempt, errors

                errors.extend(validated_result.errors or ["Agent returned non-success status"])
            except Exception as exc:
                safe_error = mask_sensitive(str(exc))
                errors.append(safe_error)
                logger.warning(
                    "Agent execution failed: %s attempt=%s error=%s",
                    agent_name,
                    attempt,
                    safe_error,
                )

        failed_result = AgentExecutionResult(
            agent_name=agent_name,
            status="FAILED",
            output={},
            confidence=0.0,
            errors=errors,
            started_at=utc_now(),
            completed_at=utc_now(),
        )
        return failed_result, attempts_allowed, errors

    def _run_with_timeout(
        self,
        entry: AgentRegistryEntry,
        context: dict[str, Any],
    ) -> AgentExecutionResult:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(entry.handler, dict(context))
        try:
            return future.result(timeout=self.timeout_seconds)
        except TimeoutError as exc:
            future.cancel()
            raise TimeoutError(
                f"Agent {entry.name} timed out after {self.timeout_seconds} seconds"
            ) from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _check_rate_limit(self, agent_name: str) -> None:
        if not self.enable_rate_limit:
            return

        now = time.monotonic()
        window_start = now - 60
        calls = [
            timestamp
            for timestamp in self._rate_limit_window.get(agent_name, [])
            if timestamp >= window_start
        ]
        if len(calls) >= self.rate_limit_per_minute:
            raise RateLimitExceeded(f"Agent rate limit exceeded for {agent_name}")
        calls.append(now)
        self._rate_limit_window[agent_name] = calls

    def _merge_agent_output(
        self,
        context: dict[str, Any],
        result: AgentExecutionResult,
    ) -> None:
        context.setdefault("agent_outputs", {})[result.agent_name] = result.output
        context.update(result.output)
        if "confidence" in result.output:
            context["confidence"] = result.output["confidence"]
        elif "confidence" not in context:
            context["confidence"] = result.confidence

    def _eval_condition_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
            left = self._eval_condition_node(node.left, context)
            right = self._eval_condition_node(node.comparators[0], context)
            op = node.ops[0]

            if isinstance(op, ast.GtE):
                return left >= right
            if isinstance(op, ast.Gt):
                return left > right
            if isinstance(op, ast.LtE):
                return left <= right
            if isinstance(op, ast.Lt):
                return left < right
            if isinstance(op, ast.Eq):
                return left == right
            if isinstance(op, ast.NotEq):
                return left != right
            if isinstance(op, ast.In):
                return left in right
            if isinstance(op, ast.NotIn):
                return left not in right

        if isinstance(node, ast.Name):
            return context.get(node.id)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self._eval_condition_node(item, context) for item in node.elts]

        raise OrchestratorEngineError("Unsupported condition expression")

    def _resolve_pipeline_path(self, pipeline_path: str | Path) -> Path:
        path = Path(pipeline_path)
        if path.is_absolute() or path.exists():
            return path

        backend_root = Path(__file__).resolve().parents[2]
        backend_relative_path = backend_root / path
        if backend_relative_path.exists():
            return backend_relative_path

        return path


def mask_sensitive(value: Any) -> Any:
    """Mask likely secret values in logs and persisted traces."""

    if isinstance(value, dict):
        masked: dict[str, Any] = {}
        for key, item in value.items():
            if SECRET_KEY_PATTERN.search(str(key)):
                masked[key] = "***MASKED***"
            else:
                masked[key] = mask_sensitive(item)
        return masked

    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]

    if isinstance(value, tuple):
        return tuple(mask_sensitive(item) for item in value)

    if isinstance(value, str):
        return SECRET_VALUE_PATTERN.sub("***MASKED***", value)

    return value


def make_trace_safe(value: Any) -> Any:
    """Convert runtime context values into JSON-safe trace content."""

    if isinstance(value, dict):
        return {
            key: make_trace_safe(item)
            for key, item in value.items()
            if key not in {"db", "report"}
        }

    if isinstance(value, list):
        return [make_trace_safe(item) for item in value]

    if isinstance(value, tuple):
        return [make_trace_safe(item) for item in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    object_id = getattr(value, "id", None) or getattr(value, "run_id", None)
    if object_id is not None:
        return {
            "type": value.__class__.__name__,
            "id": str(object_id),
        }

    return str(value)
