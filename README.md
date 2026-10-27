# cups-api-json

[![CI](https://github.com/aledv/cups-api-json/actions/workflows/ci.yml/badge.svg)](https://github.com/aledv/cups-api-json/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A tiny REST API that reports the state of a local [CUPS](https://openprinting.github.io/cups/) print server as JSON:
default printer, its status and the number of pending and completed jobs. Handy for dashboards (e.g.
Homepage's custom API widget), Home Assistant REST sensors or monitoring.

## API

`GET /cups/status`

```json
{
  "default_printer": "Office_Laser",
  "completed_jobs_count": 5,
  "pending_jobs_count": 2,
  "printer_status": "idle"
}
```

`printer_status` is one of `idle`, `processing`, `stopped`, `unknown` (state not recognised or no default printer),
`not_found` (the default printer no longer exists) or `error` (CUPS not reachable, HTTP 503).
`completed_jobs_count` counts at most `COMPLETED_JOBS_LIMIT` jobs (default 100).

`GET /health` returns `{"status": "healthy"}`. The Docker image uses it as its health check.

## Quick start

Requirements: Docker with Compose, and CUPS running on the same host.

```bash
git clone https://github.com/aledv/cups-api-json.git
cd cups-api-json
docker compose up -d --build
curl http://localhost:5001/cups/status
```

The container uses the host network to reach CUPS on `localhost:631`, so `ports:` mappings don't apply: change the
port with `PORT` instead. If CUPS only listens on its Unix socket, the compose file mounts `/run/cups/cups.sock`.

Without Compose:

```bash
docker build -t cups-api .
docker run -d --name cups-api --network host -e PORT=5001 \
  -v /run/cups/cups.sock:/run/cups/cups.sock:ro cups-api
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `5001` | Listening port |
| `CUPS_SERVER` | CUPS default | CUPS server as `host[:port]` or a socket path |
| `COMPLETED_JOBS_LIMIT` | `100` | Maximum number of completed jobs counted |

The API has no authentication: keep it on your LAN.

## Development

```bash
pip install -r requirements-dev.txt          # Flask + ruff; tests use a fake cups module
python -m unittest discover -s tests -v      # tests
ruff check . && ruff format --check .        # Python linter
hadolint Dockerfile                          # Dockerfile linter
```

Running the app itself needs `pycups` (`apt install libcups2-dev` then `pip install -r requirements.txt`) and a CUPS
server: `gunicorn --bind 0.0.0.0:5001 app:app`.

CI (GitHub Actions) runs the linters, the tests and a Docker build on every push.

## Project structure

```
app.py               Flask app (served by gunicorn in the container)
tests/test_app.py    unit tests with a fake cups module
Dockerfile           two-stage build, runs as a non-root user
docker-compose.yml   host network + optional CUPS socket mount
```

## Contributing

Issues and pull requests are welcome. Please run the linters and tests (see [Development](#development)) before opening a pull request.

## License

MIT, see [LICENSE](LICENSE).
