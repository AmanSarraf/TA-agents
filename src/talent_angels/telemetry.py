"""Optional trace exporters. The JSONL run log stays the source of truth."""

from __future__ import annotations

import os

_PHOENIX_STARTED = False


def telemetry_backend() -> str:
    return os.environ.get("TELEMETRY_BACKEND", "none").strip().lower() or "none"


def setup_telemetry() -> str:
    """Start the configured exporter. Safe to call more than once.

    ``none`` (default) does nothing. ``phoenix`` registers OpenInference so
    LiteLLM completions appear in a local Phoenix UI. Install extras first::

        pip install -e ".[phoenix]"
        phoenix serve   # other terminal, http://127.0.0.1:6006
    """
    backend = telemetry_backend()
    if backend in {"", "none"}:
        return "none"
    if backend == "phoenix":
        return _setup_phoenix()
    raise ValueError(f"Unsupported TELEMETRY_BACKEND={backend!r}; supported: none, phoenix")


def _setup_phoenix() -> str:
    global _PHOENIX_STARTED
    if _PHOENIX_STARTED:
        return "phoenix"
    try:
        from openinference.instrumentation.litellm import LiteLLMInstrumentor
        from phoenix.otel import register
    except ImportError as exc:
        raise ImportError(
            'TELEMETRY_BACKEND=phoenix requires the phoenix extra: pip install -e ".[phoenix]"'
        ) from exc

    os.environ.setdefault("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006")
    register(
        project_name=os.environ.get("PHOENIX_PROJECT_NAME", "ta-agents").strip() or "ta-agents",
        auto_instrument=False,
    )
    LiteLLMInstrumentor().instrument()
    _PHOENIX_STARTED = True
    return "phoenix"
