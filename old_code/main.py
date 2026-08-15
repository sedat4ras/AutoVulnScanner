import scanner
import analyzer
import reporter
import sys

def main():
    print("=" * 60)
    print("      🔒 CYBERSEC LAB MENTOR - AUTOMATED AUDITOR 🔒")
    print("=" * 60)

    # 1. Get Target IP
    target_ip = input("Enter Target IP (e.g., 192.168.1.5): ").strip()
    
    if not target_ip:
        print("❌ Error: IP address cannot be empty.")
        sys.exit()

    # 2. RUN SCANNER
    # This returns the specific filename created (e.g., scan_192_168...xml)
    print(f"\n[1/3] Starting Nmap Scan on {target_ip}...")
    xml_filename = scanner.scan_target(target_ip)
    
    if not xml_filename:
        print("❌ Scan failed. Exiting.")
        sys.exit()

    # 3. RUN ANALYZER
    # We pass the specific filename to the AI
    print(f"\n[2/3] Sending {xml_filename} to AI Analyst...")
    analysis_text = analyzer.analyze_results(xml_filename)
    
    if not analysis_text:
        print("❌ Analysis failed. Exiting.")
        sys.exit()

    # 4. RUN REPORTER
    # We pass the IP and the AI text to create the PDF
    print("\n[3/3] Generating PDF Report...")
    pdf_name = reporter.create_pdf(target_ip, analysis_text)

    # FINISH
    print("\n" + "=" * 60)
    print(f"🎉 PROCESS COMPLETE!")
    if pdf_name:
        print(f"📂 Your report is ready: {pdf_name}")
    print("=" * 60)

if __name__ == "__main__":
    main()