import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize Client
client = OpenAI(api_key=api_key)

def analyze_results(xml_filename):
    print("-" * 50)
    print(f"🧠 AI Analyst is reading file: {xml_filename}...")
    print("⏳ Analyzing vulnerabilities... (This consumes API credits)")
    print("-" * 50)

    # 1. Check if the specific XML file exists
    if not os.path.exists(xml_filename):
        print(f"❌ ERROR: File '{xml_filename}' not found.")
        return None

    # 2. Read the Scan Data
    try:
        with open(xml_filename, "r", encoding="utf-8", errors="ignore") as f:
            scan_data = f.read()
    except Exception as e:
        print(f"❌ READ ERROR: {e}")
        return None

    # 3. The Prompt
    system_prompt = """
    You are a Senior Cybersecurity Analyst named 'CyberSec Lab Mentor'.
    Your task is to analyze the provided Nmap scan XML data.

    Visual Style Rules:
    - Use Red Exclamation Mark emojis (❗) to indicate risk level NEXT TO the port number.
    - Low Risk: ❗ (1 mark)
    - Medium Risk: ❗❗❗ (3 marks)
    - High/Critical Risk: ❗❗❗❗❗ (5 marks)

    Output Format for each open port:
    ### Port [Number] ([Service Name]) [Risk Emojis]
    
    1. **Explanation**: What is this service?
    2. **Security Risk**: Why is it dangerous?
    3. **Remediation**: Specific commands or steps to secure it.

    Keep the tone professional, concise, and educational.
    """

    # 4. Send to OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the Nmap scan output:\n\n{scan_data}"}
            ]
        )

        # Get the analysis text
        analysis_text = response.choices[0].message.content
        
        # --- NEW: PRINT TO TERMINAL ---
        print("\n" + "=" * 60)
        print("📢  TERMINAL REPORT PREVIEW  📢")
        print("=" * 60)
        print(analysis_text)
        print("=" * 60 + "\n")
        # ------------------------------
        
        print("✅ AI Analysis complete!")
        
        # RETURN the text so the Reporter can use it
        return analysis_text

    except Exception as e:
        print(f"❌ API ERROR: {e}")
        return None