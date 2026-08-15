"""SCA Scanner - Trivy integration for dependency/container scanning"""

import subprocess
import json
from pathlib import Path


def run_trivy(target_path: str) -> dict:
    """
    Run Trivy SCA scan for vulnerable dependencies and libraries

    Args:
        target_path: Path to scan (directory with package files)

    Returns:
        Dictionary with scan results (JSON format)
    """
    print(f"\n[SCA] Scanning dependencies in {target_path} with Trivy...")

    if not Path(target_path).exists():
        print(f"  ❌ Path not found: {target_path}")
        return {}

    try:
        cmd = [
            "trivy",
            "fs",
            "--format=json",
            "--severity=HIGH,CRITICAL",
            target_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode not in [0, 1]:
            print(f"  ⚠️  Trivy warning: {result.stderr}")
            return {}

        findings = json.loads(result.stdout) if result.stdout else {"Results": []}
        vuln_count = sum(len(r.get("Vulnerabilities", [])) for r in findings.get("Results", []))
        print(f"  ✅ Found {vuln_count} vulnerable dependencies")

        return findings

    except subprocess.TimeoutExpired:
        print("  ❌ Trivy scan timed out")
        return {}
    except json.JSONDecodeError:
        print("  ❌ Failed to parse Trivy output")
        return {}
    except FileNotFoundError:
        print("  ❌ Trivy not installed. Download from: https://github.com/aquasecurity/trivy")
        return {}
    except Exception as e:
        print(f"  ❌ Trivy error: {e}")
        return {}


def format_trivy_findings(findings: dict) -> list:
    """Format Trivy results into standardized findings"""
    formatted = []

    for result in findings.get("Results", []):
        target = result.get("Target", "unknown")

        for vuln in result.get("Vulnerabilities", []):
            formatted.append({
                "type": "SCA",
                "severity": vuln.get("Severity", "MEDIUM").upper(),
                "package": vuln.get("PkgName", "unknown"),
                "version": vuln.get("InstalledVersion", "unknown"),
                "vuln_id": vuln.get("VulnerabilityID", "unknown"),
                "message": vuln.get("Title", "No description"),
                "target": target
            })

    return formatted
