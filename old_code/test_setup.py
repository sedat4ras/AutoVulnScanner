import os
import nmap
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load secrets from .env file
load_dotenv()

# 2. Check API Key
api_key = os.getenv("OPENAI_API_KEY")

print("-" * 30)
if api_key:
    # Print first few characters for verification
    print("✅ API Key found: Starts with", api_key[:7] + "...")
else:
    print("❌ ERROR: API Key could not be read! Check your .env file.")

# 3. Check Nmap
try:
    nm = nmap.PortScanner()
    print(f"✅ Nmap Version: {nm.nmap_version()} (Installed and working)")
except nmap.PortScannerError:
    print("❌ ERROR: Nmap not found on system or not in PATH.")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("-" * 30)
print("🎯 Ready for duty, Chief!")