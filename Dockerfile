# syntax=docker/dockerfile:1.7

# ---------- Stage 1: fetch third-party scanner binaries ----------
FROM debian:trixie-slim AS scanners

ARG TRIVY_VERSION=0.74.0
ARG GITLEAKS_VERSION=8.30.1

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/trivy.tgz \
      "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
 && tar -xzf /tmp/trivy.tgz -C /usr/local/bin trivy \
 && chmod +x /usr/local/bin/trivy \
 && /usr/local/bin/trivy --version

RUN curl -fsSL -o /tmp/gitleaks.tgz \
      "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
 && tar -xzf /tmp/gitleaks.tgz -C /usr/local/bin gitleaks \
 && chmod +x /usr/local/bin/gitleaks \
 && /usr/local/bin/gitleaks version


# ---------- Stage 2: install python deps into a portable prefix ----------
FROM python:3.11.16-slim-trixie AS pydeps

ARG SEMGREP_VERSION=1.174.0

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --prefix=/install \
      -r /tmp/requirements.txt \
      "semgrep==${SEMGREP_VERSION}"


# ---------- Stage 3: runtime ----------
FROM python:3.11.16-slim-trixie

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --gid 10001 shield \
 && useradd  --uid 10001 --gid shield \
              --home-dir /home/shield --create-home --shell /usr/sbin/nologin shield

COPY --from=scanners /usr/local/bin/trivy    /usr/local/bin/trivy
COPY --from=scanners /usr/local/bin/gitleaks /usr/local/bin/gitleaks
COPY --from=pydeps   /install                /usr/local

WORKDIR /app
COPY --chown=shield:shield main.py ./
COPY --chown=shield:shield src/    ./src/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

USER shield
WORKDIR /work

ENTRYPOINT ["python", "/app/main.py"]
CMD ["/work"]
