"""
Wrapper script for deploying Streamlit app on Vercel
"""
import subprocess
import sys
import os

# Set up environment
port = int(os.environ.get("PORT", 8501))

# Run Streamlit app
subprocess.run([
    sys.executable, "-m", "streamlit", "run",
    "streamlit_app.py",
    "--server.port", str(port),
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.enableCORS", "false",
    "--server.enableXsrfProtection", "false"
])