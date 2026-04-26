import socket
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os

def decrypt_data(key, iv, ciphertext):
    """
    Decrypt data using AES in CBC mode
    """
    try:
        # Decode from base64
        key = base64.b64decode(key)
        iv = base64.b64decode(iv)
        ciphertext = base64.b64decode(ciphertext)
        
        # Create cipher and decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)
        
        # Remove padding (PKCS7)
        padding_length = plaintext[-1]
        plaintext = plaintext[:-padding_length]
        
        return plaintext.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def start_server(host='127.0.0.1', port=5000):
    """
    Start the server to receive and decrypt data
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"[SERVER] Listening on {host}:{port}...")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"\n[SERVER] Connected by {client_address}")
            
            try:
                # Receive data in chunks
                data = b''
                while True:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                
                # Parse JSON containing key, IV, and ciphertext
                received_data = json.loads(data.decode('utf-8'))
                key = received_data['key']
                iv = received_data['iv']
                ciphertext = received_data['ciphertext']
                
                print("[SERVER] Received encrypted data")
                print(f"[SERVER] Key (base64): {key[:50]}...")
                print(f"[SERVER] IV (base64): {iv}")
                
                # Decrypt
                plaintext = decrypt_data(key, iv, ciphertext)
                
                if plaintext:
                    print(f"\n[SERVER] Decrypted message:\n{plaintext}\n")
                    
                    # Save to file
                    output_file = "decrypted_message.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(plaintext)
                    print(f"[SERVER] Message saved to {output_file}")
                else:
                    print("[SERVER] Decryption failed")
                    
            except json.JSONDecodeError:
                print("[SERVER] Invalid JSON format received")
            except Exception as e:
                print(f"[SERVER] Error processing data: {e}")
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
