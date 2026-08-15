import nmap
import sys
import datetime
import os

def scan_target(target_ip):
    # Initialize the Nmap PortScanner
    nm = nmap.PortScanner()
    
    print("-" * 50)
    print(f"🚀 Scanning target: {target_ip}")
    print("☕ This might take a while depending on the target scope...")
    print("-" * 50)

    try:
        # Start the Nmap Scan
        nm.scan(hosts=target_ip, arguments='-sV -T4 --open')
        
        print("✅ Scan completed successfully!")
        
        # Get raw XML output
        xml_output = nm.get_nmap_last_output()
        
        # FOLDER SETUP: Create 'scans' directory if it doesn't exist
        output_folder = "scans"
        os.makedirs(output_folder, exist_ok=True)
        
        # Create dynamic filename inside the folder
        safe_ip = target_ip.replace('.', '_')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        # Join folder and filename (e.g., scans/scan_192_168_1_5_2026...)
        filename = os.path.join(output_folder, f"scan_{safe_ip}_{timestamp}.xml")
        
        # Save to file
        with open(filename, "wb") as f:
            f.write(xml_output)
            print(f"💾 Raw scan data saved to: {filename}")
            
        # Return the FULL PATH so analyzer can find it
        return filename

    except Exception as e:
        print(f"❌ SCANNER ERROR: {e}")
        return None

if __name__ == "__main__":
    ip = input("Enter Target IP: ")
    scan_target(ip)