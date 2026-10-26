FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libcups2-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libcups2 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 cupsapi
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
WORKDIR /app
COPY app.py .
USER cupsapi
ENV PORT=5001
EXPOSE 5001
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=4)"
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --access-logfile - app:app"]
