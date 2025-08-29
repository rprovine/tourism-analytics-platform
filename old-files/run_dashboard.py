#!/usr/bin/env python3
"""
Launch the visual Tourism Analytics Dashboard
"""

import subprocess
import sys
import os

def main():
    print("🌺 Starting Tourism Analytics Visual Dashboard...")
    print("=" * 50)
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run streamlit
    try:
        print("🚀 Launching Streamlit dashboard...")
        print("📱 The dashboard will open in your browser automatically")
        print("🔗 URL: http://localhost:8501")
        print("\n💡 Make sure your FastAPI platform is running at http://localhost:8000")
        print("   If not, run: docker-compose up")
        print("\n" + "=" * 50)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app/dashboard/web_dashboard.py",
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Streamlit is installed: pip install streamlit")
        print("2. Make sure your FastAPI is running: docker-compose up")
        print("3. Try running manually: streamlit run app/dashboard/web_dashboard.py")

if __name__ == "__main__":
    main()