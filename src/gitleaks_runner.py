"""Secrets Scanner - Gitleaks integration for API keys/tokens/credentials detection"""

import subprocess
import json
from pathlib import Path


def run_gitleaks(target_path: str) -> dict:
    """
    Run Gitleaks to detect hardcoded secrets, API keys, tokens, passwords

    Args:
        target_path: Path to scan (git repo or directory)

    Returns:
        Dictionary with scan results (JSON format)
    """
    print(f"\n[Secrets] Scanning for hardcoded secrets in {target_path}...")

    if not Path(target_path).exists():
        print(f"  ❌ Path not found: {target_path}")
        return {}

    try:
        cmd = [
            "gitleaks",
            "detect",
            f"--source={target_path}",
            "--report-format=json",
            "--verbose"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Gitleaks exits with 1 if secrets found, 0 if clean
        if result.stdout:
            findings = json.loads(result.stdout)
        else:
            findings = []

        secret_count = len(findings) if isinstance(findings, list) else 0
        print(f"  ✅ Found {secret_count} potential secrets")

        return {"secrets": findings} if isinstance(findings, list) else {}

    except subprocess.TimeoutExpired:
        print("  ❌ Gitleaks scan timed out")
        return {}
    except json.JSONDecodeError:
        print("  ❌ Failed to parse Gitleaks output")
        return {}
    except FileNotFoundError:
        print("  ⚠️  Gitleaks not installed. Download from: https://github.com/gitleaks/gitleaks")
        print("     Continuing without secrets scan...")
        return {}
    except Exception as e:
        print(f"  ⚠️  Gitleaks error: {e}")
        return {}


def format_gitleaks_findings(findings: dict) -> list:
    """Format Gitleaks results into standardized findings"""
    formatted = []

    for secret in findings.get("secrets", []):
        formatted.append({
            "type": "Secret",
            "severity": "CRITICAL",  # Secrets are always critical
            "file": secret.get("File", "unknown"),
            "line": secret.get("StartLine", 0),
            "rule": secret.get("RuleID", "unknown"),
            "message": f"Potential {secret.get('Match', 'credential')} detected",
            "match": secret.get("Match", "")[:20] + "..."  # Truncate for safety
        })

    return formatted
