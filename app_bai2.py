from flask import Flask, render_template, request, jsonify, send_file
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import os
import base64

app = Flask(__name__)

# Configuration
MESSAGE_FILE = "message.txt"
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"
SIGNATURE_FILE = "signature.bin"

# Load keys on startup
private_key = None
public_key = None

def load_keys():
    global private_key, public_key
    try:
        # Load private key
        with open(PRIVATE_KEY_FILE, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        # Load public key
        with open(PUBLIC_KEY_FILE, 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read())
        
        return True
    except Exception as e:
        print(f"Error loading keys: {e}")
        return False

@app.route('/')
def index():
    return render_template('bai2_index.html')

@app.route('/api/message', methods=['GET'])
def get_message():
    try:
        if os.path.exists(MESSAGE_FILE):
            with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                message = f.read()
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': 'Message file not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/message', methods=['POST'])
def update_message():
    try:
        data = request.json
        message = data.get('message', '')
        
        with open(MESSAGE_FILE, 'w', encoding='utf-8') as f:
            f.write(message)
        
        return jsonify({'success': True, 'message': 'Message saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/sign', methods=['POST'])
def sign_message():
    global private_key
    
    if private_key is None:
        return jsonify({'success': False, 'error': 'Private key not loaded'}), 400
    
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is empty'}), 400
        
        # Sign the message
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Save signature to file
        with open(SIGNATURE_FILE, 'wb') as f:
            f.write(signature)
        
        # Return signature info
        return jsonify({
            'success': True,
            'signature_hex': signature.hex(),
            'signature_b64': base64.b64encode(signature).decode('utf-8'),
            'signature_size': len(signature),
            'message_size': len(message),
            'hash_algorithm': 'SHA-256',
            'padding': 'PSS'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/verify', methods=['POST'])
def verify_signature():
    global public_key
    
    if public_key is None:
        return jsonify({'success': False, 'error': 'Public key not loaded'}), 400
    
    try:
        data = request.json
        message = data.get('message', '')
        signature_b64 = data.get('signature', '')
        
        if not message or not signature_b64:
            return jsonify({'success': False, 'error': 'Message or signature is empty'}), 400
        
        # Decode signature from base64
        try:
            signature = base64.b64decode(signature_b64)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid base64 signature'}), 400
        
        # Verify signature
        try:
            public_key.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return jsonify({'success': True, 'valid': True, 'message': 'Signature is valid!'})
        except Exception:
            return jsonify({'success': True, 'valid': False, 'message': 'Signature verification failed!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/keys', methods=['GET'])
def get_keys():
    try:
        keys = {}
        
        if os.path.exists(PRIVATE_KEY_FILE):
            with open(PRIVATE_KEY_FILE, 'r', encoding='utf-8') as f:
                keys['private_key'] = f.read()
        
        if os.path.exists(PUBLIC_KEY_FILE):
            with open(PUBLIC_KEY_FILE, 'r', encoding='utf-8') as f:
                keys['public_key'] = f.read()
        
        return jsonify({'success': True, 'keys': keys})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    if load_keys():
        app.run(debug=True, host='127.0.0.1', port=5003)
    else:
        print("Failed to load keys!")
