import os
import time
import subprocess
import zipfile
import shutil
import sys
import socket
import asyncio

from website.func.database import dataTable

# Configuration
TOR_DIR = r"C:\tor\tor"
TOR_EXE = os.path.join(TOR_DIR, "tor.exe")
TEMPLATE_TOR_DIR = os.path.join(os.path.dirname(__file__), "tor")
HIDDEN_SERVICE_DIR = r"C:\tor\hidden_service"
TORRC_PATH = os.path.join(TOR_DIR, "torrc")
HOSTNAME_FILE = os.path.join(HIDDEN_SERVICE_DIR, "hostname")
ONION_OUT = "onion_domain.txt"
LOCAL_PORT = 8080
APP_DIR = os.path.join(os.path.dirname(__file__), "website")
APP_FILE = os.path.join(APP_DIR, "app.py")

def purple(text):
    return f"\033[95m{text}\033[0m"
def red(text):
    return f"\033[91m{text}\033[0m"
def green(text):
    return f"\033[92m{text}\033[0m"

def create_hidden_service_dir():
    if not os.path.exists(HIDDEN_SERVICE_DIR):
        print(purple(f"[*] Creating hidden service directory: {HIDDEN_SERVICE_DIR}"))
        os.makedirs(HIDDEN_SERVICE_DIR)

def create_torrc():
    if not os.path.exists(TORRC_PATH):
        print(purple(f"[*] Creating torrc file: {TORRC_PATH}"))
        config = f"""SocksPort 9050
HiddenServiceDir {HIDDEN_SERVICE_DIR}
HiddenServicePort 80 127.0.0.1:{LOCAL_PORT}
"""
        with open(TORRC_PATH, 'w') as f:
            f.write(config)

def start_tor():
    print(purple("[*] Starting Tor..."))
    return subprocess.Popen(
        [TOR_EXE, "-f", TORRC_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def is_port_open(host, port, timeout=1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False

def wait_for_onion(timeout=60):
    if os.path.exists(ONION_OUT):
        print(green("[*] .onion domain already exists. Skipping generation."))
        return
    print(purple("[*] Waiting for .onion domain to be generated..."))
    elapsed = 0
    while elapsed < timeout:
        if os.path.exists(HOSTNAME_FILE):
            with open(HOSTNAME_FILE, 'r') as f:
                onion = f.read().strip()
                print(green(f"[+] .onion domain: {onion}"))
                with open(ONION_OUT, 'w') as out:
                    out.write(onion + '\n')
                print(green(f"[+] Saved to: {ONION_OUT}"))
                return
        time.sleep(2)
        elapsed += 2
    raise TimeoutError(red("[-] Timeout: .onion domain was not generated."))

def stop_tor(proc):
    print(purple("[!] Stopping Tor..."))
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

def start_fastapi():
    print(purple("[*] Starting FastAPI..."))
    stdout = open("fastapi_stdout.log", "wb")
    stderr = open("fastapi_stderr.log", "wb")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "website.app:app", "--host", "127.0.0.1", "--port", str(LOCAL_PORT)],
        stdout=stdout,
        stderr=stderr
    )

if __name__ == "__main__":
    if not os.path.exists(TOR_EXE):
        print(red("[*] Tor not found, copying from project folder..."))
        shutil.copytree(TEMPLATE_TOR_DIR, TOR_DIR, dirs_exist_ok=True)
        print(green(f"[+] Tor installed at: {TOR_DIR}"))

    if not os.path.isdir(APP_DIR) or not os.path.isfile(APP_FILE):
        print(red("[-] Missing 'website' directory or 'app.py' file."))
        print(red("[-] Please create a 'website' folder with an 'app.py' file inside."))
        print(red("[-] For more information, refer to the README.md file."))
        exit(1)

    create_hidden_service_dir()
    create_torrc()
    tor_proc = start_tor()
    fastapi_proc = start_fastapi()

    try:
        wait_for_onion()
        print(green("[*] Tor hidden service is running!"))
        time.sleep(2)  # Give some time for FastAPI to start
        asyncio.run(dataTable())
        with open(HOSTNAME_FILE, 'r') as f:
            onion_domain = f.read().strip()
        print(purple(f"[*] Website is accessible at: {onion_domain}"))
        print(green("[*] FastAPI is running. Type 'exit' to stop."))
        while True:
            inp = input()
            if inp.strip().lower() == 'exit':
                break

    except KeyboardInterrupt:
        print(purple("\n[!] Interrupted by user."))

    finally:
        print(purple("[!] Stopping FastAPI..."))
        fastapi_proc.terminate()
        try:
            fastapi_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            fastapi_proc.kill()
        print(green("[*] FastAPI stopped."))

        stop_tor(tor_proc)
        print(green("[*] Tor process stopped."))
