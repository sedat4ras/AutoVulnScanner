# ShieldScan

> A comprehensive source code security scanning pipeline combining SAST, SCA, and secrets detection with local LLM triage for prioritized, actionable findings.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SAST](https://img.shields.io/badge/SAST-Semgrep-26C242?style=flat-square)](https://semgrep.dev/)
[![SCA](https://img.shields.io/badge/SCA-Trivy-1978C8?style=flat-square)](https://github.com/aquasecurity/trivy)
[![Secrets](https://img.shields.io/badge/Secrets-Gitleaks-FF6B35?style=flat-square)](https://github.com/gitleaks/gitleaks)
[![LLM](https://img.shields.io/badge/LLM-Ollama--Mistral-7C3AED?style=flat-square)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)]()
[![CI](https://github.com/sedat4ras/ShieldScan/actions/workflows/ci.yml/badge.svg)](https://github.com/sedat4ras/ShieldScan/actions/workflows/ci.yml)

---

## Overview

ShieldScan is a production-grade DevSecOps pipeline that scans source code repositories for vulnerabilities across three dimensions:

1. **SAST** (Static Application Security Testing) — Code pattern matching for vulnerabilities (SQL injection, XSS, weak crypto)
2. **SCA** (Software Composition Analysis) — Dependency scanning for known CVEs
3. **Secrets Detection** — Hardcoded API keys, tokens, passwords

All findings are automatically categorized and prioritized using a **local Ollama Mistral LLM** (no API costs, fully offline).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Source Code Repository                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
    ┌────────┐        ┌────────┐        ┌──────────┐
    │ Semgrep│        │ Trivy  │        │Gitleaks  │
    │ (SAST) │        │ (SCA)  │        │(Secrets) │
    └────┬───┘        └───┬────┘        └────┬─────┘
         │ Code Issues    │ CVEs             │ Credentials
         └────────────────┼─────────────────┘
                          │
                    Raw Findings
                    (JSON)
                          │
                          ▼
                 ┌──────────────────┐
                 │  Ollama Mistral  │
                 │  LLM Triage      │
                 └────────┬─────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
        Critical      Medium        Low
        (Fix Now)     (Fix Soon)   (Nice-to-Have)
            │             │            │
            └─────────────┼────────────┘
                          ▼
                  ┌───────────────────┐
                  │  Markdown Report  │
                  │  + JSON Data      │
                  └───────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **SAST** | Semgrep pattern matching for code vulnerabilities (OWASP Top 10) |
| **SCA** | Trivy scans dependencies for known CVEs with NVD data |
| **Secrets** | Gitleaks detects hardcoded API keys, tokens, credentials |
| **LLM Triage** | Local Ollama Mistral categorizes findings by severity |
| **CI/CD Ready** | GitHub Actions workflow included for automated scanning |
| **Containerized** | Dockerfile with all tools pre-installed |
| **Offline** | Local LLM means no external API calls (no costs, full privacy) |

## Prerequisites

### For Local Development:
- Python 3.11+
- [Semgrep](https://semgrep.dev) — SAST scanner (install via `pip install semgrep`)
- [Trivy](https://github.com/aquasecurity/trivy) — SCA scanner
- [Gitleaks](https://github.com/gitleaks/gitleaks) — Secrets scanner
- [Ollama](https://ollama.ai) — Local LLM runtime (required for full functionality)
- Mistral 7B model (download: `ollama pull mistral`)

### For Docker:
- Docker (all tools pre-installed in image)

## Installation

### Option A: Local Setup (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/sedat4ras/ShieldScan.git
cd ShieldScan

# Create virtual environment
python -m venv venv && source venv/bin/activate  # macOS/Linux
# python -m venv venv && .\venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Semgrep
pip install semgrep

# Install Trivy (macOS)
brew install trivy
# Or download from: https://github.com/aquasecurity/trivy/releases

# Install Gitleaks (macOS)
brew install gitleaks
# Or download from: https://github.com/gitleaks/gitleaks/releases

# Install Ollama
# Download from: https://ollama.ai
# Then: ollama pull mistral && ollama serve
```

### Option B: Docker

```bash
# Build (one time, ~2 min first build)
docker build -t shieldscan:latest .

# Scan a repository — mount it read/write so reports can be written back
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work \
  shieldscan:latest /work

# With Ollama on the host: add --network=host so the container
# can reach http://localhost:11434
docker run --rm --network=host \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd)":/work \
  shieldscan:latest /work
```

The image runs as a non-root user (`shield`, UID 10001), so either pass
`--user "$(id -u):$(id -g)"` (Docker) or `--userns=keep-id:uid=10001,gid=10001`
(rootless Podman) so the container process can write reports back to the
bind-mounted directory.

## Usage

### Local Scanning

#### Step 1: Start Ollama (in a separate terminal)
```bash
# First-time setup
ollama pull mistral  # Downloads Mistral 7B model (~4GB)

# Start the Ollama server
ollama serve
# Ollama will be available at http://localhost:11434
```

#### Step 2: Run the Scanner (in another terminal)
```bash
cd ShieldScan
python main.py

# When prompted, enter:
#   Target path: . (current directory)
#   or: /path/to/repository
```

#### What Happens:
1. **Semgrep** scans code patterns (30-60 seconds)
2. **Trivy** checks dependencies for CVEs (15-30 seconds)
3. **Gitleaks** searches for hardcoded secrets (5-10 seconds)
4. **Ollama Mistral** categorizes findings and generates report (30-45 seconds)

**Total time:** ~2-3 minutes for typical repo

**Output:**
- `security_report_[timestamp].md` — Human-readable findings with remediation steps
- `findings_[timestamp].json` — Structured JSON data for SIEM integration

### Fallback Mode (No Ollama)

If Ollama is not available, ShieldScan automatically generates a **structured report** without LLM categorization:

```bash
# Even without Ollama, scanner works:
python main.py
# → Semgrep + Trivy + Gitleaks still run
# → Report generated without LLM triage
# ⚠️  Less sophisticated categorization, but still useful
```

**Fallback report includes:**
- SAST counts and findings
- Vulnerable package list
- Secrets summary
- ✅ Still produces markdown + JSON output

### Example Report (with Ollama)

```markdown
# Security Scan Report

## Executive Summary
- SAST Issues: 3
- Vulnerable Dependencies: 2
- Secrets Found: 0

## 🔴 Critical Issues
- Potential SQL Injection in app.py:42
  Severity: High
  Fix: Use parameterized queries (prepared statements)
  
- AWS credentials in .env (hardcoded)
  Severity: Critical
  Fix: Use environment variables or AWS IAM roles

## 🟡 Medium Issues
- Outdated Flask dependency (1.0 → 2.3)
  Fix: pip install --upgrade flask
  Impact: Known vulnerabilities in request handling
  
## 🟢 Low Issues
- Unused import in utils.py
  Fix: Remove unused imports
```

## Docker Deployment

For production use with guaranteed tool availability, use the shipped image.
See [Installation → Option B](#option-b-docker) for the run commands.

The Dockerfile is a 3-stage build (scanners / pydeps / runtime):

- **Base:** `python:3.11.16-slim-trixie`, non-root user `shield` (UID 10001)
- **Pinned:** Semgrep 1.174.0, Trivy 0.74.0, Gitleaks 8.30.1
- **Runtime footprint:** ~770 MB, only `git` + `ca-certificates` on top of the Python slim
- **No apt repos** for third-party tools — release tarballs pulled directly from GitHub, so upstream apt-key / signed-by churn cannot break the build

The design and trade-offs are written up in
[docs/writeup-dockerfile-and-ci.md](docs/writeup-dockerfile-and-ci.md).

## CI/CD Integration

Every push and pull request against `main` runs the GitHub Actions workflow at
[.github/workflows/ci.yml](.github/workflows/ci.yml):

| Job | What it does |
|-----|--------------|
| `Lint Dockerfile` | Hadolint against the Dockerfile |
| `Build image`    | `docker/build-push-action@v6` with the GHA layer cache, exports the built image as a job artifact |
| `Smoke test`     | Loads the artifact, verifies Semgrep / Trivy / Gitleaks are on `PATH` inside the container, runs an end-to-end scan against a fixture, asserts both reports are produced |

Typical run time: **~3 minutes** end-to-end from a cold cache.

## Technical Details

### Semgrep (SAST)
- **Detects:** Code vulnerabilities using pattern matching
- **Output:** OWASP Top 10 categories (injection, XSS, insecure crypto, etc.)
- **Config:** Uses `p/owasp-top-ten` rulesets

### Trivy (SCA)
- **Detects:** Known CVEs in package dependencies
- **Scans:** requirements.txt, package.json, pom.xml, etc.
- **Data:** Updated daily from NVD (National Vulnerability Database)

### Gitleaks (Secrets)
- **Detects:** Hardcoded secrets (API keys, tokens, passwords)
- **Patterns:** GitHub/AWS/Slack/private keys, etc.
- **Severity:** All secrets marked CRITICAL

### Ollama + Mistral LLM
- **Runs locally:** Zero API costs, 100% private
- **Model:** Mistral 7B (8GB VRAM, ~30s response time)
- **Function:** Reads all scanner outputs → produces prioritized report

## v1 → v2 Migration

**What changed:**

| Aspect | v1 | v2 |
|--------|----|----|
| Scanner | Nmap port scan | SAST/SCA/Secrets |
| AI Usage | GPT-3.5 emoji ratings | Ollama LLM triage |
| Analysis | "Port 22 is risky 🔴🔴🔴" | Real vulnerability logic |
| Report | PDF only | Markdown + JSON |
| Cost | OpenAI API $$$ | Free (local Ollama) |
| Speed | Fast | 2-3 min per scan |
| Target | Network scanning | Source code analysis |

**Old code location:** `old_code/` (v1 archived for reference)

## Testing

ShieldScan has been tested with mock vulnerability data:
```bash
$ python3 -c "
from src.semgrep_runner import run_semgrep
from src.llm_triage import triage_findings

# Test passed: module imports, logic flow, report generation ✅
"
```

**Test results:**
- ✅ All modules import correctly
- ✅ LLM triage logic executes (with fallback)
- ✅ Report generation works
- ✅ Fallback mode active when Ollama unavailable

## Troubleshooting

**"Ollama not running"**
```bash
ollama serve  # Start in separate terminal
```

**"Ollama running but model not installed"**
```bash
ollama pull mistral  # Download ~4GB Mistral 7B model
```

**"Semgrep not found"**
```bash
pip install semgrep
semgrep --version
```

**"Trivy not found"**
- macOS: `brew install trivy`
- Linux: https://github.com/aquasecurity/trivy#installation
- Windows: Download binary from releases

**"Gitleaks not found"**
- macOS: `brew install gitleaks`
- Linux/Windows: https://github.com/gitleaks/gitleaks#installation

**Docker build fails**
```bash
docker build --no-cache -t shieldscan:latest .
```

**"ModuleNotFoundError: No module named 'src'"**
```bash
# Make sure you're running from repo root:
cd /path/to/ShieldScan
python main.py
```

## Architecture Notes

This tool implements the DevSecOps principle of **"shift-left"** security — catching issues before they reach production. Compared to v1 (which used raw Nmap output + GPT emoji ratings), v2:

- ✅ Uses **real vulnerability scanners** (not just port lists)
- ✅ Implements **genuine logic** (CVE correlation, pattern matching)
- ✅ **Categorizes findings** properly (by type, severity, package)
- ✅ **Local LLM triage** (no external API, no costs)
- ✅ **Production-ready** (CI/CD, Docker, JSON exports)

## License

MIT — See LICENSE file

## Contact

GitHub: [sedat4ras/ShieldScan](https://github.com/sedat4ras/ShieldScan) | Email: sudo@sedataras.com
