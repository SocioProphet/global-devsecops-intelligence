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
import os, subprocess, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


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

_state = {"last_rc": None, "last_ts": 0, "runs": 0, "fails": 0}
_lock = threading.Lock()


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


def main() -> None:
    threading.Thread(target=_run_validators, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()


if __name__ == "__main__":
    main()
