"""Optional telemetry exporters stay off by default."""

from __future__ import annotations

import pytest

from talent_angels.telemetry import setup_telemetry, telemetry_backend


def test_default_backend_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEMETRY_BACKEND", raising=False)
    assert telemetry_backend() == "none"
    assert setup_telemetry() == "none"


def test_unknown_backend_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEMETRY_BACKEND", "langsmith")
    with pytest.raises(ValueError, match="Unsupported TELEMETRY_BACKEND"):
        setup_telemetry()


def test_phoenix_without_extra_explains_install(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEMETRY_BACKEND", "phoenix")
    monkeypatch.setattr("talent_angels.telemetry._PHOENIX_STARTED", False)
    try:
        import openinference.instrumentation.litellm  # noqa: F401
        import phoenix.otel  # noqa: F401
    except ImportError:
        with pytest.raises(ImportError, match="phoenix extra"):
            setup_telemetry()
        return
    pytest.skip("phoenix extra is installed in this environment")
