"""
AutoVulnScanner v2 - SAST/SCA/Secrets Pipeline with Local LLM Triage
Analyzes source code repositories for security vulnerabilities using:
  - Semgrep (SAST - code patterns)
  - Trivy (SCA - vulnerable dependencies)
  - Gitleaks (Secrets - hardcoded credentials)
  - Ollama Mistral (LLM triage - categorization & prioritization)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from src.semgrep_runner import run_semgrep, format_semgrep_findings
from src.trivy_runner import run_trivy, format_trivy_findings
from src.gitleaks_runner import run_gitleaks, format_gitleaks_findings
from src.llm_triage import triage_findings, check_ollama_connection


def main():
    print("=" * 70)
    print(" 🔒 AutoVulnScanner v2 - Security Pipeline (SAST/SCA/Secrets) 🔒")
    print("=" * 70)

    # 1. Get target path
    print("\nEnter target path to scan (file/directory/git repo):")
    print("  Example: . (current dir), /path/to/repo, ./src")
    target = input("Target path: ").strip() or "."

    if not Path(target).exists():
        print(f"❌ Error: Path '{target}' not found")
        sys.exit(1)

    # 2. Verify Ollama availability
    print("\n[Setup] Checking dependencies...")
    ollama_ok = check_ollama_connection()
    if not ollama_ok:
        print("  ⚠️  Ollama not running. Install: https://ollama.ai")
        print("     To enable LLM triage: ollama pull mistral && ollama serve")
        print("     Continuing with fallback mode...\n")
    else:
        print("  ✅ Ollama Mistral ready")

    # 3. Run all scanners
    print("\n[Scan] Running security scanners...\n")

    findings_raw = {
        "sast": run_semgrep(target),
        "sca": run_trivy(target),
        "secrets": run_gitleaks(target)
    }

    # 4. Format findings
    sast_formatted = format_semgrep_findings(findings_raw["sast"])
    sca_formatted = format_trivy_findings(findings_raw["sca"])
    secrets_formatted = format_gitleaks_findings(findings_raw["secrets"])

    all_findings = {
        "sast": sast_formatted,
        "sca": sca_formatted,
        "secrets": secrets_formatted
    }

    # 5. LLM triage
    print("\n[Report] Generating security report...")
    report = triage_findings(all_findings)

    # 6. Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"security_report_{timestamp}.md"
    json_file = f"findings_{timestamp}.json"

    with open(report_file, "w") as f:
        f.write(report)

    with open(json_file, "w") as f:
        json.dump(all_findings, f, indent=2)

    # 7. Print summary
    total = len(sast_formatted) + len(sca_formatted) + len(secrets_formatted)
    print("\n" + "=" * 70)
    print(f"✅ SCAN COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  SAST Issues:    {len(sast_formatted)}")
    print(f"  SCA Vulns:      {len(sca_formatted)}")
    print(f"  Secrets:        {len(secrets_formatted)}")
    print(f"  TOTAL:          {total}")
    print(f"\n📄 Reports:")
    print(f"  Markdown: {report_file}")
    print(f"  JSON:     {json_file}")
    print("=" * 70)

    # 8. Print report preview
    print("\n📋 REPORT PREVIEW:\n")
    print(report)


if __name__ == "__main__":
    main()
