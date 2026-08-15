"""LLM Triage Layer - Use local Ollama (Mistral) to categorize and prioritize findings"""

import requests
import json
from typing import Dict, List


OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"


def check_ollama_connection() -> bool:
    """Verify Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def triage_findings(all_findings: Dict) -> str:
    """
    Use Ollama Mistral to analyze and categorize security findings

    Args:
        all_findings: Dictionary with 'sast', 'sca', 'secrets' findings

    Returns:
        Human-readable markdown report
    """
    if not check_ollama_connection():
        print("\n⚠️  Ollama not running! Using fallback summary.")
        return generate_fallback_report(all_findings)

    print("\n[Triage] Analyzing findings with Ollama Mistral...")

    # Build prompt
    prompt = build_triage_prompt(all_findings)

    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Error: No response from Ollama")
        else:
            print(f"  ❌ Ollama error: {response.status_code}")
            return generate_fallback_report(all_findings)

    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to Ollama. Is it running?")
        print("     Start Ollama: ollama serve")
        return generate_fallback_report(all_findings)
    except Exception as e:
        print(f"  ❌ LLM triage error: {e}")
        return generate_fallback_report(all_findings)


def build_triage_prompt(findings: Dict) -> str:
    """Build structured prompt for LLM analysis"""
    sast_items = findings.get("sast", [])
    sca_items = findings.get("sca", [])
    secrets = findings.get("secrets", [])

    prompt = f"""You are a professional cybersecurity analyst. Analyze these security scan findings and create a prioritized report.

**STATIC ANALYSIS (SAST)** - Code vulnerabilities:
{json.dumps(sast_items[:5], indent=2) if sast_items else "None found"}

**DEPENDENCY SCAN (SCA)** - Vulnerable packages:
{json.dumps(sca_items[:5], indent=2) if sca_items else "None found"}

**SECRETS DETECTION** - Hardcoded credentials:
{json.dumps(secrets[:5], indent=2) if secrets else "None found"}

Create a professional security report with:
1. Executive Summary (severity overview)
2. Critical Issues (🔴 - must fix immediately)
3. Medium Issues (🟡 - fix soon)
4. Low Issues (🟢 - nice to have)
5. Remediation Actions (specific steps)

Be concise, technical, and actionable. Use markdown formatting.
Focus on real risk, not noise. Omit false positives."""

    return prompt


def generate_fallback_report(findings: Dict) -> str:
    """Generate basic report if Ollama unavailable"""
    sast = findings.get("sast", [])
    sca = findings.get("sca", [])
    secrets = findings.get("secrets", [])

    report = f"""# Security Scan Report

## Summary
- **SAST Issues**: {len(sast)}
- **Vulnerable Dependencies**: {len(sca)}
- **Secrets Found**: {len(secrets)}

## 🔴 Critical Issues
{f"{len(secrets)} hardcoded secrets detected!" if secrets else "None"}

## 🟡 Medium Issues
"""
    if sca:
        report += f"\n### Vulnerable Dependencies ({len(sca)})\n"
        for item in sca[:5]:
            report += f"- {item.get('package', '?')}: {item.get('message', '')}\n"

    if sast:
        report += f"\n### Code Issues ({len(sast)})\n"
        for item in sast[:5]:
            report += f"- {item.get('file', '?')}: {item.get('message', '')}\n"

    report += "\n## Recommendation\nRun this scan with Ollama for detailed analysis: `ollama pull mistral && ollama serve`"

    return report
