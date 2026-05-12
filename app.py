from flask import Flask, render_template, request, jsonify
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import base64

app = Flask(__name__)

# Global variables to store keys
private_key = None
public_key = None
private_key_pem = None
public_key_pem = None

@app.route('/')
def index():
    return render_template('rsa_index.html')

@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    global private_key, public_key, private_key_pem, public_key_pem
    
    try:
        # Generate RSA private key (2048-bit)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return jsonify({
            'success': True,
            'private_key': private_key_pem,
            'public_key': public_key_pem
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/sign-message', methods=['POST'])
def sign_message():
    global private_key
    
    if private_key is None:
        return jsonify({'success': False, 'error': 'Keys not generated yet'}), 400
    
    try:
        data = request.json
        message = data.get('message', '').encode('utf-8')
        
        # Sign the message
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encode signature to base64 for display
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': message.decode('utf-8'),
            'signature': signature_b64,
            'signature_hex': signature.hex()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/verify-signature', methods=['POST'])
def verify_signature():
    global public_key
    
    if public_key is None:
        return jsonify({'success': False, 'error': 'Keys not generated yet'}), 400
    
    try:
        data = request.json
        message = data.get('message', '').encode('utf-8')
        signature_b64 = data.get('signature', '')
        
        # Decode signature from base64
        signature = base64.b64decode(signature_b64)
        
        # Verify the signature
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return jsonify({'success': True, 'valid': True, 'message': 'Signature is valid!'})
    except Exception as e:
        return jsonify({'success': True, 'valid': False, 'message': f'Signature verification failed: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)
