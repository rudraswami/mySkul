"""
Test the new modular FastAPI structure on port 8002
"""
import subprocess
import sys
import os

# Set PYTHONPATH to include the backend directory
os.environ['PYTHONPATH'] = '/app/backend'

# Change to backend directory
os.chdir('/app/backend')

# Start the new modular app on port 8002 for testing
try:
    print("🚀 Starting modular FastAPI app on port 8002 for testing...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8002", 
        "--reload"
    ])
except KeyboardInterrupt:
    print("\n✅ Modular app stopped")
