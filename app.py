"""Small REST API exposing the state of a local CUPS server as JSON."""

import logging
import os

import cups
from flask import Flask, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("cups-api")

# CUPS printer-state values (RFC 8011): 3 idle, 4 processing, 5 stopped
PRINTER_STATES = {3: "idle", 4: "processing", 5: "stopped"}
COMPLETED_JOBS_LIMIT = int(os.environ.get("COMPLETED_JOBS_LIMIT", "100"))


def connect():
    """Connection to CUPS. CUPS_SERVER (host[:port] or socket path) overrides the default."""
    server = os.environ.get("CUPS_SERVER")
    if server:
        cups.setServer(server)
    return cups.Connection()


def printer_status(conn, printer):
    if not printer:
        return "unknown"
    info = conn.getPrinters().get(printer)
    if info is None:
        return "not_found"
    return PRINTER_STATES.get(info.get("printer-state"), "unknown")


def job_counts(conn):
    """(completed, pending). Completed jobs are capped at COMPLETED_JOBS_LIMIT."""
    pending = len(conn.getJobs(which_jobs="not-completed"))
    completed = len(conn.getJobs(which_jobs="completed", limit=COMPLETED_JOBS_LIMIT))
    return completed, pending


def error_response():
    return jsonify(
        {
            "error": "CUPS not reachable",
            "default_printer": None,
            "completed_jobs_count": 0,
            "pending_jobs_count": 0,
            "printer_status": "error",
        }
    ), 503


@app.get("/cups/status")
def cups_status():
    try:
        conn = connect()
        printer = conn.getDefault()
        completed, pending = job_counts(conn)
        status = printer_status(conn, printer)
    except Exception:
        # Details go to the log only, never to the client.
        log.exception("CUPS query failed")
        return error_response()
    return jsonify(
        {
            "default_printer": printer,
            "completed_jobs_count": completed,
            "pending_jobs_count": pending,
            "printer_status": status,
        }
    )


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})
