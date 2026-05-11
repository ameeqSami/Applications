"""
run.py — Flask server launcher.

Usage:
    python run.py

Then open http://127.0.0.1:8000 in your browser.
"""
import sys
import os

# Add the project directory to path
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

if __name__ == "__main__":
    from api import app
    print("🚀 Starting Flask server on http://127.0.0.1:8000 ...")
    print("📝 Open http://127.0.0.1:8000 in your browser.")
    print("⏹️  Press Ctrl+C to stop the server.\n")
    app.run(host="127.0.0.1", port=8000, debug=True)
