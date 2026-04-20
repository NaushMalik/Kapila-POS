"""
Kapila Invoice - Remote Access Server
Run this file to start both Flask and create a public URL for mobile access
"""
import subprocess
import sys
import time
import os

def install_and_run():
    print("=" * 50)
    print("KAPILA INVOICE - MOBILE ACCESS")
    print("=" * 50)
    print()
    
    # Check if Flask is running
    print("[1] Starting Flask server on port 5001...")
    flask_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    print("    Waiting for Flask to start...")
    time.sleep(5)
    print("    Flask started!")
    print()
    
    # Start localtunnel
    print("[2] Creating public URL...")
    print("    This may take 10-20 seconds...")
    print()
    
    try:
        # Run localtunnel
        result = subprocess.run(
            ["npx", "--yes", "localtunnel", "--port", "5001"],
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.TimeoutExpired:
        print("Timeout - let me try again...")
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Alternative: Please open a NEW terminal and run:")
        print("    npx localtunnel --port 5001")
    
    print()
    print("Keep this window open to maintain the connection!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    install_and_run()

