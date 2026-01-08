\# 🛡️ AutoVulnScanner (AI-Powered Auditor)



\*\*AutoVulnScanner\*\* is an automated vulnerability assessment tool that bridges the gap between raw network scanning and actionable intelligence. It leverages \*\*Nmap\*\* for discovery and \*\*OpenAI (GPT)\*\* for intelligent threat analysis, culminating in a professional PDF report.



\## 🚀 Features



\* \*\*Automated Scanning:\*\* Executes Nmap scans with version detection (`-sV`).

\* \*\*AI Analysis:\*\* Uses GPT-3.5/4 to interpret open ports and suggest remediation.

\* \*\*Risk Scoring:\*\* Visual risk assessment (❗ Low to ❗❗❗❗❗ Critical).

\* \*\*PDF Reporting:\*\* Generates clean, executive-ready PDF reports.

\* \*\*Organized Output:\*\* Automatically manages scan logs and report files.



\## 🛠️ Installation



1\.  \*\*Clone the repository:\*\*

&nbsp;   ```bash

&nbsp;   git clone \[https://github.com/sedat4ras/AutoVulnScanner.git](https://github.com/KULLANICI\_ADIN/AutoVulnScanner.git)

&nbsp;   cd AutoVulnScanner

&nbsp;   ```



2\.  \*\*Install dependencies:\*\*

&nbsp;   ```bash

&nbsp;   pip install -r requirements.txt

&nbsp;   ```



3\.  \*\*Install Nmap:\*\*

&nbsp;   \* Ensure Nmap is installed on your system and added to PATH.

&nbsp;   \* (Windows users must install Npcap).



4\.  \*\*Setup API Key:\*\*

&nbsp;   \* Create a `.env` file in the root directory.

&nbsp;   \* Add your OpenAI API key:

&nbsp;       ```text

&nbsp;       OPENAI\_API\_KEY=sk-your\_api\_key\_here

&nbsp;       ```



\## 💻 Usage



Run the main script and follow the prompts:



```bash

python main.py



Enter the target IP address (e.g., 192.168.1.5).



Wait for the scan and AI analysis to complete.



Find your report in the reports/ folder.



⚠️ Disclaimer

This tool is designed for educational purposes and authorized security testing only. Do not use this tool on networks or systems you do not own or do not have explicit permission to test. The author is not responsible for any misuse.





