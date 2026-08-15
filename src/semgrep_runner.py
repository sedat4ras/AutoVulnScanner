"""SAST Scanner - Semgrep integration for code pattern matching"""

import subprocess
import json
import sys
from pathlib import Path


def run_semgrep(target_path: str, config: str = "p/owasp-top-ten") -> dict:
    """
    Run Semgrep SAST scan on target repository/directory

    Args:
        target_path: Path to scan (file or directory)
        config: Semgrep config (default: OWASP Top Ten patterns)

    Returns:
        Dictionary with scan results (JSON format)
    """
    print(f"\n[SAST] Scanning {target_path} with Semgrep...")

    if not Path(target_path).exists():
        print(f"  ❌ Path not found: {target_path}")
        return {}

    try:
        cmd = [
            "semgrep",
            "--json",
            f"--config={config}",
            target_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode not in [0, 1]:  # 0 = no issues, 1 = issues found
            print(f"  ⚠️  Semgrep warning: {result.stderr}")
            return {}

        findings = json.loads(result.stdout) if result.stdout else {"results": []}
        issue_count = len(findings.get("results", []))
        print(f"  ✅ Found {issue_count} SAST issues")

        return findings

    except subprocess.TimeoutExpired:
        print("  ❌ Semgrep scan timed out")
        return {}
    except json.JSONDecodeError:
        print("  ❌ Failed to parse Semgrep output")
        return {}
    except FileNotFoundError:
        print("  ❌ Semgrep not installed. Run: pip install semgrep")
        return {}
    except Exception as e:
        print(f"  ❌ Semgrep error: {e}")
        return {}


def format_semgrep_findings(findings: dict) -> list:
    """Format Semgrep results into standardized findings"""
    formatted = []

    for result in findings.get("results", []):
        formatted.append({
            "type": "SAST",
            "severity": result.get("extra", {}).get("severity", "MEDIUM").upper(),
            "file": result.get("path", "unknown"),
            "line": result.get("start", {}).get("line", 0),
            "rule": result.get("check_id", "unknown"),
            "message": result.get("extra", {}).get("message", "No description"),
            "code": result.get("extra", {}).get("lines", "")
        })

    return formatted
