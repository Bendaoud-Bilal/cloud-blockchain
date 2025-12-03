#!/usr/bin/env python3
"""
Blockchain Network Stop Script
Cross-platform Python alternative to stop-blockchain.cmd
Works on Windows, macOS, and Linux
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=False, 
                                capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("=" * 50)
    print("   Stopping Blockchain Network (Python)")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Stop and remove containers
    run_command("docker-compose down", "Stopping and removing containers")
    
    print("\nBlockchain network stopped.")
    print("\nTo also remove volumes (blockchain data), run:")
    print("  docker-compose down -v")
    print("\nOr use Python:")
    print("  python -c \"import subprocess; subprocess.run('docker-compose down -v', shell=True)\"")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
