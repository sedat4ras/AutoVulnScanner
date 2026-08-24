"""Secrets Scanner - Gitleaks integration for API keys/tokens/credentials detection"""

import json
import subprocess
import tempfile
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
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "gitleaks.json"

            # `dir` scans the working tree; the removed `detect` subcommand only
            # ever read git history. Gitleaks writes JSON to --report-path, not
            # to stdout, so the report is read back from disk.
            cmd = [
                "gitleaks",
                "dir",
                f"--report-path={report_path}",
                "--report-format=json",
                "--no-banner",
                target_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # 0 = clean, 1 = leaks found; anything else is a real failure.
            if result.returncode not in (0, 1):
                print(f"  ⚠️  Gitleaks failed: {result.stderr.strip()}")
                return {}

            findings = json.loads(report_path.read_text()) if report_path.exists() else []

        if not isinstance(findings, list):
            print("  ❌ Unexpected Gitleaks report shape")
            return {}

        print(f"  ✅ Found {len(findings)} potential secrets")
        return {"secrets": findings}

    except subprocess.TimeoutExpired:
        print("  ❌ Gitleaks scan timed out")
        return {}
    except json.JSONDecodeError:
        print("  ❌ Failed to parse Gitleaks report")
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
