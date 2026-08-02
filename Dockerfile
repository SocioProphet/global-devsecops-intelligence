# GDI — AI4IT ops-intelligence validation profile, served continuously.
# Runs the repo's real validators (make validate) on a schedule and exposes
# /healthz + /metrics on :8840 for the prophet-platform deployment. No :latest;
# CI publishes an immutable sha- tag.
FROM python:3.12-slim

# `make validate` needs make; keep the layer minimal.
RUN apt-get update && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# non-root to match the deployment securityContext (runAsUser 65532)
RUN useradd -u 65532 -m gdi && chown -R gdi /app
USER 65532

EXPOSE 8840
ENV PORT=8840
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','8840'); sys.exit(0 if urllib.request.urlopen(f'http://localhost:{p}/healthz', timeout=3).status==200 else 1)" || exit 1
CMD ["python", "serve.py"]
