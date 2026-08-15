FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Semgrep
RUN python -m pip install --no-cache-dir semgrep

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && apt-get install -y trivy && \
    rm -rf /var/lib/apt/lists/*

# Install Gitleaks
RUN wget -O /tmp/gitleaks https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks-linux-x64 && \
    chmod +x /tmp/gitleaks && \
    mv /tmp/gitleaks /usr/local/bin/gitleaks

# Setup working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure src is importable
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command
ENTRYPOINT ["python", "main.py"]
