#!/usr/bin/env python3
"""
Reset Blockchain Script

This script resets the blockchain on all deployed nodes.
It clears all Redis data (chain, transactions, nodes) and reinitializes with genesis block.

Usage:
    python reset_blockchain.py --nodes https://node1.onrender.com,https://node2.onrender.com
    python reset_blockchain.py --nodes https://node1.onrender.com --secret your-reset-secret

For local Docker:
    python reset_blockchain.py --nodes http://localhost:5001,http://localhost:5002,http://localhost:5003
"""

import argparse
import requests
import sys


def reset_node(node_url: str, secret: str) -> bool:
    """Reset a single blockchain node."""
    try:
        print(f"\n🔄 Resetting {node_url}...")
        
        response = requests.post(
            f"{node_url}/reset",
            json={"secret": secret},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"   ✅ {node_url} reset successfully!")
            return True
        elif response.status_code == 403:
            print(f"   ❌ {node_url}: Invalid secret key")
            return False
        elif response.status_code == 500:
            print(f"   ⚠️  {node_url}: Redis not connected (in-memory only)")
            return False
        else:
            print(f"   ❌ {node_url}: Error {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {node_url}: Connection refused (is the node running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ {node_url}: Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ {node_url}: {str(e)}")
        return False


def verify_reset(node_url: str) -> bool:
    """Verify that the node was reset by checking chain length."""
    try:
        response = requests.get(f"{node_url}/chain", timeout=10)
        if response.status_code == 200:
            data = response.json()
            chain_length = data.get("length", 0)
            if chain_length == 1:
                print(f"   ✓ Verified: Chain length is 1 (genesis block only)")
                return True
            else:
                print(f"   ⚠️  Warning: Chain length is {chain_length}")
                return False
    except Exception as e:
        print(f"   ⚠️  Could not verify: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Reset blockchain on all nodes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Reset Render nodes:
    python reset_blockchain.py --nodes https://blockchain-node1.onrender.com,https://blockchain-node2.onrender.com

  Reset local Docker nodes:
    python reset_blockchain.py --nodes http://localhost:5001,http://localhost:5002,http://localhost:5003

  With custom secret:
    python reset_blockchain.py --nodes http://localhost:5001 --secret my-secret-key
        """
    )
    
    parser.add_argument(
        "--nodes",
        required=True,
        help="Comma-separated list of node URLs (e.g., https://node1.onrender.com,https://node2.onrender.com)"
    )
    
    parser.add_argument(
        "--secret",
        default="blockchain-reset-secret",
        help="Reset secret key (default: blockchain-reset-secret). On Render, each node has its own auto-generated secret."
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify reset by checking chain length after reset"
    )
    
    args = parser.parse_args()
    
    # Parse node URLs
    nodes = [n.strip() for n in args.nodes.split(",") if n.strip()]
    
    if not nodes:
        print("❌ No nodes specified!")
        sys.exit(1)
    
    print("=" * 60)
    print("🔗 Blockchain Reset Script")
    print("=" * 60)
    print(f"\nNodes to reset: {len(nodes)}")
    for node in nodes:
        print(f"  • {node}")
    
    # Confirm before proceeding
    print("\n⚠️  WARNING: This will permanently delete all blockchain data!")
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != "RESET":
        print("\n❌ Aborted.")
        sys.exit(0)
    
    # Reset each node
    success_count = 0
    for node in nodes:
        if reset_node(node, args.secret):
            success_count += 1
            if args.verify:
                verify_reset(node)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Summary: {success_count}/{len(nodes)} nodes reset successfully")
    print("=" * 60)
    
    if success_count < len(nodes):
        print("\n⚠️  Some nodes failed to reset.")
        print("   Make sure the correct secret is provided for each node.")
        print("   On Render, each node has a different auto-generated RESET_SECRET.")
        sys.exit(1)
    else:
        print("\n✅ All nodes reset successfully!")
        print("\nNext steps:")
        print("  1. Nodes will auto-register with peers in ~10 seconds")
        print("  2. You can manually register nodes if needed: POST /nodes/register")
        sys.exit(0)


if __name__ == "__main__":
    main()
