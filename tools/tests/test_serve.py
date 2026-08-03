"""Tests for the serve.py runtime: crash-safe env parsing + Prometheus
exposition format + readiness logic + the GDI-2c mesh HTTP ingest. Loads serve.py
by path (repo root)."""
import http.client
import importlib.util
import json
import os
import threading
from http.server import ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_spec = importlib.util.spec_from_file_location("gdi_serve", os.path.join(ROOT, "serve.py"))
serve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(serve)


def _serve_and_post(path, body, *, mesh_enabled, headers=None):
    """Start serve.H on an ephemeral port, POST once, return (status, body)."""
    serve.MESH_ENABLED = mesh_enabled
    serve._BUS = serve.InMemoryBus()  # fresh bus per call
    srv = ThreadingHTTPServer(("127.0.0.1", 0), serve.H)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        payload = body if isinstance(body, (bytes, str)) else json.dumps(body)
        conn.request("POST", path, body=payload, headers=headers or {})
        resp = conn.getresponse()
        return resp.status, resp.read()
    finally:
        srv.shutdown()


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


# --- GDI-2c: mesh HTTP ingest --------------------------------------------------

_EVENT = {
    "timestamp": 1785628800000, "utc_timestamp": "2026-08-02T00:00:00.000Z",
    "type": "meshrush_slot_fill", "data": {"n_filled": 1, "n_refused": 0, "fills": [], "refused": []},
}


def test_ingest_publishes_to_bus_when_enabled():
    status, body = _serve_and_post(
        "/mesh/telemetry", _EVENT, mesh_enabled=True,
        headers={"Content-Length": str(len(json.dumps(_EVENT)))},
    )
    assert status == 202
    assert "accepted" in json.loads(body)
    assert len(serve._BUS.poll()) == 1  # the event is on the bus


def test_ingest_is_disabled_by_default():
    status, _ = _serve_and_post(
        "/mesh/telemetry", _EVENT, mesh_enabled=False,
        headers={"Content-Length": str(len(json.dumps(_EVENT)))},
    )
    assert status == 503


def test_ingest_rejects_non_json():
    status, _ = _serve_and_post(
        "/mesh/telemetry", "{not json", mesh_enabled=True,
        headers={"Content-Length": str(len("{not json"))},
    )
    assert status == 400
    assert len(serve._BUS.poll()) == 0  # junk never reached the bus


def test_ingest_rejects_oversized_body():
    serve.MESH_MAX_BODY = 10  # tiny cap for the test
    try:
        status, _ = _serve_and_post(
            "/mesh/telemetry", _EVENT, mesh_enabled=True,
            headers={"Content-Length": str(len(json.dumps(_EVENT)))},
        )
        assert status == 413
    finally:
        serve.MESH_MAX_BODY = 1 << 20


def test_mesh_bus_pending_metric_present():
    serve._BUS = serve.InMemoryBus()
    serve._BUS.publish_telemetry(json.dumps(_EVENT))
    assert "gdi_mesh_bus_pending 1" in serve._metrics()
