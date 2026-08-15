# AutoVulnScanner v2

> A comprehensive source code security scanning pipeline combining SAST, SCA, and secrets detection with local LLM triage for prioritized, actionable findings.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![SAST](https://img.shields.io/badge/SAST-Semgrep-26C242?style=flat-square)](https://semgrep.dev/)
[![SCA](https://img.shields.io/badge/SCA-Trivy-1978C8?style=flat-square)](https://github.com/aquasecurity/trivy)
[![Secrets](https://img.shields.io/badge/Secrets-Gitleaks-FF6B35?style=flat-square)](https://github.com/gitleaks/gitleaks)
[![LLM](https://img.shields.io/badge/LLM-Ollama--Mistral-7C3AED?style=flat-square)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)]()

---

## Overview

AutoVulnScanner v2 is a production-grade DevSecOps pipeline that scans source code repositories for vulnerabilities across three dimensions:

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
- [Semgrep](https://semgrep.dev) — SAST scanner
- [Trivy](https://github.com/aquasecurity/trivy) — SCA scanner
- [Gitleaks](https://github.com/gitleaks/gitleaks) — Secrets scanner
- [Ollama](https://ollama.ai) — Local LLM runtime
- Mistral 7B model (auto-downloaded by Ollama)

### For Docker:
- Docker (all tools pre-installed in image)

## Installation

### Option A: Local Setup (Recommended for Development)

```bash
# Clone repository
git clone https://github.com/sedat4ras/AutoVulnScanner.git
cd AutoVulnScanner

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
docker build -t autovulnscanner:v2 .
docker run --interactive autovulnscanner:v2 /path/to/repo
```

## Usage

### Local Scanning

```bash
# Start Ollama in a separate terminal
ollama serve

# In another terminal, run the scanner
python main.py
# Enter target path when prompted (e.g., . for current directory)
```

**Output:**
- `security_report_[timestamp].md` — Human-readable findings with remediation steps
- `findings_[timestamp].json` — Structured JSON data for SIEM integration

### Example Report

```markdown
# Security Scan Report

## Executive Summary
- SAST Issues: 3
- Vulnerable Dependencies: 2
- Secrets Found: 0

## 🔴 Critical Issues
- Potential SQL Injection in app.py:42
  Fix: Use parameterized queries

## 🟡 Medium Issues
- Outdated flask dependency (1.0 → 2.3)
  Fix: pip install --upgrade flask
```

## GitHub Actions Integration

The included `.github/workflows/security-scan.yml` automatically:
1. Runs on every `push` to main/develop
2. Scans your code with all three scanners
3. Posts results as PR comment
4. Uploads reports as CI artifacts

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

## Troubleshooting

**"Ollama not running"**
```bash
ollama serve  # Start in separate terminal
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

**Docker build fails**
```bash
docker build --no-cache -t autovulnscanner:v2 .
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

GitHub: [sedat4ras](https://github.com/sedat4ras) | Email: sudo@sedataras.com
