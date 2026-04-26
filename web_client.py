from flask import Flask, render_template, request, jsonify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import socket
import json
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def add_padding(data, block_size=16):
    """Add PKCS7 padding to data"""
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding

def encrypt_data(plaintext):
    """
    Encrypt data using AES in CBC mode
    Returns: key (base64), iv (base64), ciphertext (base64)
    """
    try:
        # Convert plaintext to bytes if it's a string
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generate random AES key (256 bits) and IV (128 bits)
        key = get_random_bytes(32)  # 256-bit key
        iv = get_random_bytes(16)   # 128-bit IV
        
        # Add PKCS7 padding
        plaintext = add_padding(plaintext)
        
        # Create cipher and encrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(plaintext)
        
        # Encode to base64 for transmission
        key_b64 = base64.b64encode(key).decode('utf-8')
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
        
        return key_b64, iv_b64, ciphertext_b64
    except Exception as e:
        print(f"Encryption error: {e}")
        return None, None, None

def send_to_server(key, iv, ciphertext, host='127.0.0.1', port=5000):
    """Send encrypted data to server"""
    try:
        # Prepare data packet
        data_packet = {
            'key': key,
            'iv': iv,
            'ciphertext': ciphertext
        }
        
        # Connect and send to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        client_socket.connect((host, port))
        
        # Send encrypted data as JSON
        json_data = json.dumps(data_packet)
        client_socket.sendall(json_data.encode('utf-8'))
        
        client_socket.close()
        return True, "Dữ liệu đã được gửi thành công!"
    except ConnectionRefusedError:
        return False, f"Lỗi kết nối: Server không hoạt động trên {host}:{port}"
    except socket.timeout:
        return False, f"Timeout: Không thể kết nối đến {host}:{port}"
    except Exception as e:
        return False, f"Lỗi: {str(e)}"

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/encrypt-text', methods=['POST'])
def encrypt_text():
    """API endpoint to encrypt text"""
    try:
        data = request.get_json()
        plaintext = data.get('text', '')
        server_host = data.get('host', '127.0.0.1')
        server_port = int(data.get('port', 5000))
        
        if not plaintext:
            return jsonify({'success': False, 'message': 'Vui lòng nhập tin nhắn'}), 400
        
        # Encrypt
        key, iv, ciphertext = encrypt_data(plaintext)
        
        if key is None:
            return jsonify({'success': False, 'message': 'Lỗi mã hóa'}), 500
        
        # Send to server
        success, message = send_to_server(key, iv, ciphertext, server_host, server_port)
        
        response = {
            'success': success,
            'message': message,
            'encrypted': {
                'key': key[:50] + '...',
                'iv': iv,
                'ciphertext': ciphertext[:50] + '...',
                'original_length': len(plaintext)
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/api/encrypt-file', methods=['POST'])
def encrypt_file():
    """API endpoint to encrypt file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Không có file được upload'}), 400
        
        file = request.files['file']
        server_host = request.form.get('host', '127.0.0.1')
        server_port = int(request.form.get('port', 5000))
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
        
        # Read file content
        file_content = file.read().decode('utf-8', errors='ignore')
        
        # Encrypt
        key, iv, ciphertext = encrypt_data(file_content)
        
        if key is None:
            return jsonify({'success': False, 'message': 'Lỗi mã hóa'}), 500
        
        # Send to server
        success, message = send_to_server(key, iv, ciphertext, server_host, server_port)
        
        response = {
            'success': success,
            'message': message,
            'encrypted': {
                'filename': file.filename,
                'key': key[:50] + '...',
                'iv': iv,
                'ciphertext': ciphertext[:50] + '...',
                'file_size': len(file_content)
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Web Client on http://127.0.0.1:5001")
    print("Make sure server.py is running on another terminal!")
    app.run(host='127.0.0.1', port=5001, debug=True)
