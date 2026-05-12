import subprocess
import sys
import time

requirements = [
    "Flask==2.3.2",
    "Flask-CORS==4.0.0",
    "pydantic<2.0.0",
    "requests"
]

def install_with_retry(package, max_retries=5):
    for i in range(max_retries):
        print(f"Installing {package} (Attempt {i+1}/{max_retries})...", flush=True)
        # Use Popen to see output in real-time if needed, but for simplicity we'll just check return code
        process = subprocess.run([sys.executable, "-m", "pip", "install", package, "--default-timeout=1000"])
        if process.returncode == 0:
            print(f"Successfully installed {package}", flush=True)
            return True
        else:
            print(f"Failed to install {package}.", flush=True)
            time.sleep(5)
    return False

def main():
    for req in requirements:
        if not install_with_retry(req):
            print(f"Could not install {req} after multiple attempts.", flush=True)
            sys.exit(1)
    print("All requirements installed successfully.", flush=True)

if __name__ == "__main__":
    main()
