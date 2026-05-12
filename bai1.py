from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def main():
    # Generate RSA private key (2048-bit)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save private key to PEM file
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Get public key
    public_key = private_key.public_key()

    # Save public key to PEM file
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Sign a message using the private key
    message = b"Hello World"
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Save signature to binary file
    with open("signature.bin", "wb") as f:
        f.write(signature)

    print("RSA key pair generated and saved to private_key.pem and public_key.pem")
    print("Message 'Hello World' signed and signature saved to signature.bin")

if __name__ == "__main__":
    main()