#!/usr/bin/env python3
"""GDI service entrypoint — runs the repo's real validators on a schedule and
exposes health + Prometheus metrics on :$PORT (default 8840), satisfying the
prophet-platform deployment contract (/healthz, /metrics).

This is deliberately honest: GDI is a validation-profile repo, not a fake HTTP
API. The service continuously runs `make validate` (manifest, service-desk-
metrics, model-fabric-release-readiness, github-footprint-itops, client-runtime-
dump-exposure, operational-exhaust-fusion, resource-contract-telemetry) and
publishes pass/fail as metrics. The mesh consumer/producer loop (consume
/telemetry, produce /ops/findings as RCA-claim EventEnvelopes) is layered on top
of this same validation core — see MESH_* env — and is the next increment.

Stdlib only (keeps requirements.txt to PyYAML+pytest).
"""
import json, os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_HERE = os.path.dirname(os.path.abspath(__file__))
# GDI-2c: reuse the mesh transport/consume core for the in-process bus + HTTP ingest.
sys.path.insert(0, os.path.join(_HERE, "tools"))
from mesh_consume import InMemoryBus, consume  # noqa: E402


def _int_env(key: str, default: int) -> int:
    """Parse an int env var, falling back to default on a malformed value so a
    bad PORT/INTERVAL can never crash the service before it serves /healthz."""
    try:
        return int(os.environ.get(key, str(default)))
    except (ValueError, TypeError):
        sys.stderr.write(f"[gdi] invalid {key}={os.environ.get(key)!r}, using {default}\n")
        return default


PORT = _int_env("PORT", 8840)
INTERVAL_S = _int_env("GDI_VALIDATE_INTERVAL_S", 300)
# Mesh consume->produce loop (GDI-2), OFF by default so deployment behaviour is
# unchanged until an operator opts in with MESH_ENABLED=1 (+ MESH_INPUT_DIR/MESH_OUTPUT_DIR).
MESH_ENABLED = os.environ.get("MESH_ENABLED", "0").strip().lower() not in ("", "0", "false", "no")
MESH_INTERVAL_S = _int_env("MESH_INTERVAL_S", 60)
# GDI-2c: cap the HTTP telemetry body (fail-closed against oversized posts).
MESH_MAX_BODY = _int_env("MESH_MAX_BODY", 1 << 20)

_state = {"last_rc": None, "last_ts": 0, "runs": 0, "fails": 0}
_mesh = {"runs": 0, "consumed": 0, "produced": 0, "rejected": 0, "last_ts": 0}
_lock = threading.Lock()

# GDI-2c: the in-process bus behind POST /mesh/telemetry (the agentplane live wire).
# agentplane POSTs telemetry -> published here -> drained by the mesh loop with the
# same consume() contract. No networked broker is pinned (sovereign).
_BUS = InMemoryBus()
_mesh_schema_cache = None


def _mesh_schema() -> dict:
    """Load (and cache) the event-envelope schema; path-anchored, cwd-independent."""
    global _mesh_schema_cache
    if _mesh_schema_cache is None:
        path = os.path.join(_HERE, "open-ai4it-spec/contracts/schemas/event-envelope.schema.json")
        with open(path, encoding="utf-8") as fh:
            _mesh_schema_cache = json.load(fh)
    return _mesh_schema_cache


def _mesh_loop() -> None:
    """Run the mesh consume->produce loop on an interval (opt-in via MESH_ENABLED)."""
    while True:
        try:
            r = subprocess.run(["python3", "tools/mesh_consume.py"], cwd=os.path.dirname(__file__) or ".",
                               capture_output=True, text=True, timeout=300)
            stats = None
            for line in (r.stdout or "").splitlines():
                if line.startswith("STATS "):
                    try:
                        stats = json.loads(line[len("STATS "):])
                    except json.JSONDecodeError:
                        stats = None
            with _lock:
                _mesh["runs"] += 1
                _mesh["last_ts"] = int(time.time())
                if isinstance(stats, dict):
                    for k in ("consumed", "produced", "rejected"):
                        _mesh[k] += int(stats.get(k, 0))
                else:
                    sys.stderr.write("[gdi] mesh_consume: no parseable STATS line\n")
            if r.returncode != 0:
                sys.stderr.write(f"[gdi] mesh_consume rc={r.returncode}\n{r.stderr[-2000:]}\n")
        except Exception as e:
            sys.stderr.write(f"[gdi] mesh_consume errored: {e}\n")
        # GDI-2c: also drain the in-process bus (HTTP-ingested telemetry), same contract.
        try:
            bstats = consume(_BUS, _mesh_schema())
            with _lock:
                for k in ("consumed", "produced", "rejected"):
                    _mesh[k] += int(bstats.get(k, 0))
        except Exception as e:
            sys.stderr.write(f"[gdi] mesh bus drain errored: {e}\n")
        time.sleep(MESH_INTERVAL_S)


def _run_validators() -> None:
    while True:
        try:
            r = subprocess.run(["make", "validate"], cwd=os.path.dirname(__file__) or ".",
                               capture_output=True, text=True, timeout=600)
            rc = r.returncode
            if rc != 0:  # emit detail so a failed run is debuggable from pod logs
                sys.stderr.write(f"[gdi] make validate failed rc={rc}\n"
                                 f"{r.stdout[-4000:]}\n{r.stderr[-2000:]}\n")
        except Exception as e:
            rc = 2
            sys.stderr.write(f"[gdi] make validate errored: {e}\n")
        with _lock:
            _state["last_rc"] = rc
            _state["last_ts"] = int(time.time())
            _state["runs"] += 1
            if rc != 0:
                _state["fails"] += 1
        time.sleep(INTERVAL_S)


def _metrics() -> str:
    with _lock:
        s = dict(_state)
    ready = 1 if s["last_rc"] == 0 else 0
    return (
        "# HELP gdi_up 1 if the last validator run passed.\n"
        "# TYPE gdi_up gauge\n"
        f"gdi_up {ready}\n"
        "# HELP gdi_validate_runs_total total validator runs.\n"
        "# TYPE gdi_validate_runs_total counter\n"
        f"gdi_validate_runs_total {s['runs']}\n"
        "# HELP gdi_validate_failures_total validator runs that failed.\n"
        "# TYPE gdi_validate_failures_total counter\n"
        f"gdi_validate_failures_total {s['fails']}\n"
        "# HELP gdi_last_run_timestamp_seconds unix ts of the last validator run.\n"
        "# TYPE gdi_last_run_timestamp_seconds gauge\n"
        f"gdi_last_run_timestamp_seconds {s['last_ts']}\n"
        + _mesh_metrics()
    )


def _mesh_metrics() -> str:
    with _lock:
        m = dict(_mesh)
    return (
        "# HELP gdi_mesh_enabled 1 if the mesh consume loop is enabled.\n"
        "# TYPE gdi_mesh_enabled gauge\n"
        f"gdi_mesh_enabled {1 if MESH_ENABLED else 0}\n"
        "# HELP gdi_mesh_consumed_total telemetry events consumed.\n"
        "# TYPE gdi_mesh_consumed_total counter\n"
        f"gdi_mesh_consumed_total {m['consumed']}\n"
        "# HELP gdi_mesh_produced_total ops findings produced.\n"
        "# TYPE gdi_mesh_produced_total counter\n"
        f"gdi_mesh_produced_total {m['produced']}\n"
        "# HELP gdi_mesh_rejected_total telemetry events rejected (fail-closed).\n"
        "# TYPE gdi_mesh_rejected_total counter\n"
        f"gdi_mesh_rejected_total {m['rejected']}\n"
        "# HELP gdi_mesh_bus_pending telemetry envelopes on the in-process bus awaiting drain.\n"
        "# TYPE gdi_mesh_bus_pending gauge\n"
        f"gdi_mesh_bus_pending {len(_BUS.poll())}\n"
    )


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        if self.path == "/healthz":
            # ready once at least one validation run has completed
            with _lock:
                ok = _state["last_ts"] > 0
            body, code = (b'{"status":"ok"}\n' if ok else b'{"status":"starting"}\n'), (200 if ok else 503)
            self.send_response(code); self.send_header("Content-Type", "application/json")
            self.end_headers(); self.wfile.write(body)
        elif self.path == "/metrics":
            body = _metrics().encode()
            self.send_response(200); self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

    def _drain(self) -> None:
        """Discard any unread request body so closing the socket sends FIN, not RST.

        A rejection (503/413/400) that replies WITHOUT reading the posted body leaves bytes in
        the kernel receive buffer; on close the OS sends RST instead of FIN, and the client sees
        ``ConnectionResetError`` mid-read instead of the response we just sent — intermittently,
        depending on delivery timing. A real telemetry producer POSTing to a disabled endpoint
        would hit the same reset, not a clean 503. Draining fixes it at the source.

        Bounded to MESH_MAX_BODY + 64 KiB: a normal or slightly-oversized body is drained in full
        (no reset), while a pathologically huge body is not read to completion (the 413 DoS guard
        still holds — the remainder is discarded on close). Idempotent: a path that already read
        the body sets ``_body_consumed`` and this returns immediately, so it never blocks waiting
        for bytes that were already consumed.
        """
        if getattr(self, "_body_consumed", False):
            return
        self._body_consumed = True
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except (ValueError, TypeError):
            return
        remaining = min(max(length, 0), MESH_MAX_BODY + (1 << 16))
        while remaining > 0:
            chunk = self.rfile.read(min(remaining, 1 << 16))
            if not chunk:
                break
            remaining -= len(chunk)

    def _reply(self, code: int, obj: dict) -> None:
        self._drain()  # never RST a client that is still reading the response we send below
        body = (json.dumps(obj) + "\n").encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        # GDI-2c: agentplane (or any producer) posts a telemetry EventEnvelope here;
        # it is published onto the in-process bus and drained by the mesh loop under
        # the same fail-closed consume() contract. Off unless MESH_ENABLED.
        if self.path != "/mesh/telemetry":
            self._drain(); self.send_response(404); self.end_headers(); return
        if not MESH_ENABLED:
            self._reply(503, {"error": "mesh disabled"}); return
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
        except (ValueError, TypeError):
            length = -1
        if length <= 0:
            self._reply(400, {"error": "missing/invalid Content-Length"}); return
        if length > MESH_MAX_BODY:
            self._reply(413, {"error": f"body exceeds {MESH_MAX_BODY} bytes"}); return
        body = self.rfile.read(length)
        self._body_consumed = True  # body now read; _reply()'s drain becomes a no-op
        # Edge guard: reject blatantly non-JSON at ingest (envelope validation still
        # happens fail-closed at consume time); don't let junk fill the bus.
        try:
            json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self._reply(400, {"error": "body is not valid JSON"}); return
        msg_id = _BUS.publish_telemetry(body)
        self._reply(202, {"accepted": msg_id})


def main() -> None:
    threading.Thread(target=_run_validators, daemon=True).start()
    if MESH_ENABLED:
        threading.Thread(target=_mesh_loop, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
