"""Tests for the serve.py runtime: crash-safe env parsing + Prometheus
exposition format + readiness logic. Loads serve.py by path (repo root)."""
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location("gdi_serve", os.path.join(ROOT, "serve.py"))
serve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(serve)


def test_int_env_falls_back_on_malformed():
    os.environ["GDI_TEST_BAD"] = "not-an-int"
    assert serve._int_env("GDI_TEST_BAD", 7) == 7
    os.environ["GDI_TEST_OK"] = "42"
    assert serve._int_env("GDI_TEST_OK", 7) == 42
    assert serve._int_env("GDI_TEST_ABSENT", 9) == 9


def test_metrics_are_valid_prometheus_exposition():
    with serve._lock:
        serve._state.update(last_rc=0, last_ts=123, runs=5, fails=1)
    m = serve._metrics()
    assert "gdi_up 1" in m
    assert "gdi_validate_runs_total 5" in m
    assert "gdi_validate_failures_total 1" in m
    # every non-comment line must parse as "metric_name <float>"
    for line in m.strip().splitlines():
        if line and not line.startswith("#"):
            name, value = line.split()
            assert name and float(value) is not None


def test_gdi_up_reflects_last_rc():
    with serve._lock:
        serve._state.update(last_rc=1)
    assert "gdi_up 0" in serve._metrics()
    with serve._lock:
        serve._state.update(last_rc=0)
    assert "gdi_up 1" in serve._metrics()
