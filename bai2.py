#!/usr/bin/env python3
"""
Bài 2: Xác minh chữ ký bằng khóa công khai
Mô tả: Ký một thông điệp bằng khóa bí mật RSA
Yêu cầu:
• Đọc nội dung từ file văn bản message.txt
• Ký nội dung bằng thuật toán SHA-256 với khóa bí mật
• Lưu chữ ký vào file signature.bin
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os
import sys

def read_message(filename):
    """Read message from text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        return None
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return None

def load_private_key(filename):
    """Load RSA private key from PEM file"""
    try:
        with open(filename, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
        return private_key
    except FileNotFoundError:
        print(f"[ERROR] Private key file not found: {filename}")
        return None
    except Exception as e:
        print(f"[ERROR] Error loading private key: {e}")
        return None

def sign_message(message, private_key):
    """Sign message using RSA private key with SHA-256"""
    try:
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    except Exception as e:
        print(f"[ERROR] Error signing message: {e}")
        return None

def save_signature(signature, filename):
    """Save signature to binary file"""
    try:
        with open(filename, 'wb') as f:
            f.write(signature)
        return True
    except Exception as e:
        print(f"[ERROR] Error saving signature: {e}")
        return False

def main():
    print("=" * 50)
    print("  RSA Digital Signature (SHA-256)")
    print("  Buoi 6 - Bai 2")
    print("=" * 50)
    print()

    # Configuration
    message_file = "message.txt"
    private_key_file = "private_key.pem"
    signature_file = "signature.bin"

    print("[*] Configuration:")
    print(f"    Message file: {message_file}")
    print(f"    Private key file: {private_key_file}")
    print(f"    Signature output: {signature_file}")
    print()

    # Read message
    print(f"[*] Reading message from {message_file}")
    message = read_message(message_file)
    if message is None:
        print("[ERROR] Failed to read message!")
        return False
    print(f"[+] Message read successfully ({len(message)} bytes)")
    print(f"[+] Message content: {message}")
    print()

    # Load private key
    print(f"[*] Loading private key from {private_key_file}")
    private_key = load_private_key(private_key_file)
    if private_key is None:
        print("[ERROR] Failed to load private key!")
        return False
    print("[+] Private key loaded successfully")
    print()

    # Sign message
    print("[*] Signing message with RSA private key (SHA-256)...")
    signature = sign_message(message, private_key)
    if signature is None:
        print("[ERROR] Failed to sign message!")
        return False
    print(f"[+] Message signed successfully ({len(signature)} bytes)")
    print()

    # Save signature
    print(f"[*] Saving signature to {signature_file}")
    if not save_signature(signature, signature_file):
        print("[ERROR] Failed to save signature!")
        return False
    print(f"[+] Signature saved successfully")
    print()

    # Print signature in hex format
    print("[+] Signature (hex):")
    print(f"    {signature.hex()}")
    print()

    # Print file information
    sig_size = os.path.getsize(signature_file)
    print("[+] File information:")
    print(f"    Message size: {len(message)} bytes")
    print(f"    Signature size: {sig_size} bytes")
    print()

    print("[SUCCESS] Message signed and signature saved!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
