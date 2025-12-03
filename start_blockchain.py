#!/usr/bin/env python3
"""
Blockchain Network Startup Script
Cross-platform Python alternative to start-blockchain.cmd
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import time
import os

try:
    import requests
except ImportError:
    print("Installing requests library...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def run_command(command, description, check=True):
    """Run a shell command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                                capture_output=True, text=True)
        if result.returncode != 0 and check:
            print(f"ERROR: {result.stderr}")
            return False
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        return False


def register_nodes():
    """Register all nodes with each other"""
    registrations = [
        ("http://localhost:5001/nodes/register", "nodes=http://node2:5000,http://node3:5000", "Node 1"),
        ("http://localhost:5002/nodes/register", "nodes=http://node1:5000,http://node3:5000", "Node 2"),
        ("http://localhost:5003/nodes/register", "nodes=http://node1:5000,http://node2:5000", "Node 3"),
    ]
    
    for url, data, node_name in registrations:
        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 201:
                print(f"  - {node_name}: registered successfully")
            else:
                print(f"  - {node_name}: registration failed ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"  - {node_name}: connection failed - {e}")


def main():
    print("=" * 50)
    print("   Blockchain Network Startup Script (Python)")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nWorking directory: {script_dir}")
    
    # Step 1: Build Docker images
    print("\n[1/4] Building Docker images...")
    if not run_command("docker-compose build", "Building containers"):
        print("\nERROR: Failed to build images. Is Docker Desktop running?")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Step 2: Start containers
    print("\n[2/4] Starting containers...")
    if not run_command("docker-compose up -d", "Starting containers"):
        print("\nERROR: Failed to start containers.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Step 3: Wait for containers to initialize
    print("\n[3/4] Waiting for containers to initialize...")
    for i in range(5, 0, -1):
        print(f"  Waiting {i} seconds...", end='\r')
        time.sleep(1)
    print("  Containers should be ready now.")
    
    # Step 4: Register nodes
    print("\n[4/4] Registering nodes with each other...")
    register_nodes()
    
    # Success message
    print("\n" + "=" * 50)
    print("   Blockchain Network is Ready!")
    print("=" * 50)
    print("\nAccess Points:")
    print("  Wallet Client: http://localhost:8081")
    print("  Node 1:        http://localhost:5001")
    print("  Node 2:        http://localhost:5002")
    print("  Node 3:        http://localhost:5003")
    print("\nQuick Commands:")
    print("  View containers:  docker ps")
    print("  View logs:        docker-compose logs -f")
    print("  Stop network:     docker-compose down")
    print("  Stop (Python):    python stop_blockchain.py")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
