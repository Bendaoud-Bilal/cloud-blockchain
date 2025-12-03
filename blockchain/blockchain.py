'''
title           : blockchain.py
description     : A blockchain implemenation
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.6 (Cloud-Ready)
usage           : python blockchain.py
                  python blockchain.py -p 5000
                  python blockchain.py --port 5000
                  gunicorn --bind 0.0.0.0:$PORT blockchain:app
python_version  : 3.9+
Comments        : The blockchain implementation is mostly based on [1]. 
                  Modified for cloud deployment with HTTPS support.
References      : [1] https://github.com/dvf/blockchain/blob/master/blockchain.py
                  [2] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict
import binascii
import hashlib
import json
import os
import threading
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 2


class Blockchain:

    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        # Generate random number to be used as node_id
        self.node_id = str(uuid4()).replace('-', '')
        # Create genesis block
        self.create_block(0, '00')

    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        Stores full URL with protocol for HTTPS support
        """
        if not node_url:
            return
            
        parsed_url = urlparse(node_url)
        
        if parsed_url.scheme and parsed_url.netloc:
            # Full URL provided (e.g., https://node1.onrender.com)
            full_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            self.nodes.add(full_url)
        elif parsed_url.netloc:
            # URL without scheme, default to https for cloud
            self.nodes.add(f"https://{parsed_url.netloc}")
        elif parsed_url.path:
            # Just host:port format
            path = parsed_url.path
            if path.startswith('http'):
                self.nodes.add(path)
            elif ':' in path:
                # Local docker format like node1:5000
                self.nodes.add(f"http://{path}")
            else:
                self.nodes.add(f"https://{path}")
        else:
            raise ValueError('Invalid URL')


    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))


    def submit_transaction(self, sender_address, recipient_address, value, signature):
        """
        Add a transaction to transactions array if the signature verified
        """
        transaction = OrderedDict({'sender_address': sender_address, 
                                    'recipient_address': recipient_address,
                                    'value': value})

        # Reward for mining a block
        if sender_address == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        # Manages transactions from wallet to another wallet
        else:
            transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)
            if transaction_verification:
                # Check if transaction already exists (avoid duplicates from broadcasting)
                for existing_tx in self.transactions:
                    if (existing_tx['sender_address'] == sender_address and 
                        existing_tx['recipient_address'] == recipient_address and
                        existing_tx['value'] == value):
                        return len(self.chain) + 1  # Already exists, don't add again
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False

    def broadcast_transaction(self, sender_address, recipient_address, value, signature):
        """
        Broadcast a transaction to all registered nodes
        """
        for node in self.nodes:
            try:
                url = f'{node}/transactions/receive'
                requests.post(url, data={
                    'sender_address': sender_address,
                    'recipient_address': recipient_address,
                    'amount': value,
                    'signature': signature
                }, timeout=10)
            except Exception as e:
                print(f"Failed to broadcast to {node}: {e}")

    def sync_pending_transactions(self):
        """
        Sync pending transactions from all registered nodes
        """
        for node in self.nodes:
            try:
                response = requests.get(f'{node}/transactions/get', timeout=10)
                if response.status_code == 200:
                    node_transactions = response.json().get('transactions', [])
                    for tx in node_transactions:
                        # Check if transaction already exists
                        exists = False
                        for existing_tx in self.transactions:
                            if (existing_tx['sender_address'] == tx['sender_address'] and 
                                existing_tx['recipient_address'] == tx['recipient_address'] and
                                existing_tx['value'] == tx['value']):
                                exists = True
                                break
                        if not exists and tx.get('sender_address') != MINING_SENDER:
                            self.transactions.append(OrderedDict({
                                'sender_address': tx['sender_address'],
                                'recipient_address': tx['recipient_address'],
                                'value': tx['value']
                            }))
            except Exception as e:
                print(f"Failed to sync from {node}: {e}")


    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the blockchain
        """
        block = {'block_number': len(self.chain) + 1,
                'timestamp': time(),
                'transactions': self.transactions,
                'nonce': nonce,
                'previous_hash': previous_hash}

        # Reset the current list of transactions
        self.transactions = []

        self.chain.append(block)
        return block


    def hash(self, block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()


    def proof_of_work(self):
        """
        Proof of work algorithm
        """
        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        nonce = 0
        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce


    def valid_proof(self, transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess = (str(transactions)+str(last_hash)+str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0'*difficulty


    def valid_chain(self, chain):
        """
        check if a bockchain is valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            #print(last_block)
            #print(block)
            #print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            #Delete the reward transaction
            transactions = block['transactions'][:-1]
            # Need to make sure that the dictionary is ordered. Otherwise we'll get a different hash
            transaction_elements = ['sender_address', 'recipient_address', 'value']
            transactions = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in transactions]

            if not self.valid_proof(transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            try:
                print(f'{node}/chain')
                response = requests.get(f'{node}/chain', timeout=10)

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Check if the length is longer and the chain is valid
                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except Exception as e:
                print(f"Failed to get chain from {node}: {e}")

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False


# Instantiate the Node
app = Flask(__name__)
CORS(app)

# Instantiate the Blockchain
blockchain = Blockchain()


def register_with_peers():
    """
    Auto-register this node with all configured peer nodes on startup
    """
    import time as time_module
    time_module.sleep(10)  # Wait for other services to start
    
    peer_nodes = os.environ.get('PEER_NODES', '')
    own_url = os.environ.get('OWN_URL', '')
    
    if not peer_nodes:
        print("No PEER_NODES configured, skipping auto-registration")
        return
    
    peers = [p.strip() for p in peer_nodes.split(',') if p.strip()]
    
    for peer in peers:
        try:
            # Register peer with this node
            blockchain.register_node(peer)
            print(f"Added peer: {peer}")
            
            # Register this node with the peer (if OWN_URL is set)
            if own_url:
                response = requests.post(
                    f'{peer}/nodes/register-peer',
                    json={'peer_url': own_url},
                    timeout=15
                )
                if response.status_code in [200, 201]:
                    print(f"Successfully registered with peer: {peer}")
                else:
                    print(f"Failed to register with peer {peer}: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to peer {peer}: {e}")

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/configure')
def configure():
    return render_template('./configure.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'node_id': blockchain.node_id,
        'chain_length': len(blockchain.chain),
        'pending_transactions': len(blockchain.transactions),
        'registered_nodes': len(blockchain.nodes)
    }), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form

    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    transaction_result = blockchain.submit_transaction(values['sender_address'], values['recipient_address'], values['amount'], values['signature'])

    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        # Broadcast transaction to all other nodes
        blockchain.broadcast_transaction(
            values['sender_address'], 
            values['recipient_address'], 
            values['amount'], 
            values['signature']
        )
        response = {'message': 'Transaction will be added to Block '+ str(transaction_result)}
        return jsonify(response), 201

@app.route('/transactions/receive', methods=['POST'])
def receive_transaction():
    """
    Receive a broadcasted transaction from another node
    """
    values = request.form

    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # Add transaction without broadcasting again (to avoid infinite loop)
    transaction_result = blockchain.submit_transaction(
        values['sender_address'], 
        values['recipient_address'], 
        values['amount'], 
        values['signature']
    )

    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction received'}
        return jsonify(response), 201

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    # First sync pending transactions from all nodes before mining
    blockchain.sync_pending_transactions()

    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.chain[-1]
    nonce = blockchain.proof_of_work()

    # We must receive a reward for finding the proof.
    blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=blockchain.node_id, value=MINING_REWARD, signature="")

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(nonce, previous_hash)

    # Notify all nodes to sync their chains
    for node in blockchain.nodes:
        try:
            requests.get(f'{node}/nodes/resolve', timeout=10)
        except Exception as e:
            print(f"Failed to notify {node}: {e}")

    response = {
        'message': "New Block Forged",
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('nodes').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in blockchain.nodes],
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

@app.route('/nodes/register-peer', methods=['POST'])
def register_peer():
    """
    Endpoint for a peer to register itself with this node
    """
    values = request.json or request.form
    peer_url = values.get('peer_url')
    
    if not peer_url:
        return jsonify({'error': 'Please supply a peer_url'}), 400
    
    try:
        blockchain.register_node(peer_url)
        return jsonify({
            'message': 'Peer registered successfully',
            'total_nodes': list(blockchain.nodes)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/reset', methods=['POST'])
def reset_blockchain():
    """
    Reset the blockchain (clear all data)
    Requires a secret key for security
    """
    values = request.json or request.form
    secret = values.get('secret')
    expected_secret = os.environ.get('RESET_SECRET', 'blockchain-reset-secret')
    
    if secret != expected_secret:
        return jsonify({'error': 'Invalid secret'}), 403
    
    # Reinitialize blockchain
    blockchain.chain = []
    blockchain.transactions = []
    blockchain.nodes = set()
    blockchain.create_block(0, '00')
    
    return jsonify({'message': 'Blockchain reset successfully'}), 200


# Start peer registration in background when app starts
peer_thread = threading.Thread(target=register_with_peers, daemon=True)
peer_thread.start()


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    
    # Render provides PORT env variable
    port = int(os.environ.get('PORT', args.port))
    
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    
    app.run(host=host, port=port)








