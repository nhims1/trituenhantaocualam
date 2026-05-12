#include <openssl/evp.h>
#include <openssl/pem.h>
#include <openssl/rsa.h>
#include <iostream>

int main() {
    // Create context for RSA key generation
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, NULL);
    if (!ctx) {
        std::cerr << "Error creating EVP_PKEY context" << std::endl;
        return 1;
    }

    // Initialize key generation
    if (EVP_PKEY_keygen_init(ctx) <= 0) {
        std::cerr << "Error initializing key generation" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return 1;
    }

    // Set RSA key size to 2048 bits
    if (EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048) <= 0) {
        std::cerr << "Error setting RSA key size" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return 1;
    }

    // Generate the key pair
    EVP_PKEY *pkey = NULL;
    if (EVP_PKEY_keygen(ctx, &pkey) <= 0) {
        std::cerr << "Error generating RSA key pair" << std::endl;
        EVP_PKEY_CTX_free(ctx);
        return 1;
    }

    EVP_PKEY_CTX_free(ctx);

    // Save private key to file
    FILE *priv_file = fopen("private_key.pem", "wb");
    if (!priv_file) {
        std::cerr << "Error opening private key file" << std::endl;
        EVP_PKEY_free(pkey);
        return 1;
    }
    PEM_write_PrivateKey(priv_file, pkey, NULL, NULL, 0, NULL, NULL);
    fclose(priv_file);

    // Save public key to file
    FILE *pub_file = fopen("public_key.pem", "wb");
    if (!pub_file) {
        std::cerr << "Error opening public key file" << std::endl;
        EVP_PKEY_free(pkey);
        return 1;
    }
    PEM_write_PUBKEY(pub_file, pkey);
    fclose(pub_file);

    // Clean up
    EVP_PKEY_free(pkey);

    std::cout << "RSA key pair generated and saved to private_key.pem and public_key.pem" << std::endl;

    // Now sign a message using the private key
    std::string message = "Hello World";
    unsigned char *signature = NULL;
    size_t sig_len = 0;

    // Load private key for signing
    FILE *priv_file_sign = fopen("private_key.pem", "rb");
    if (!priv_file_sign) {
        std::cerr << "Error opening private key for signing" << std::endl;
        return 1;
    }
    EVP_PKEY *priv_key = PEM_read_PrivateKey(priv_file_sign, NULL, NULL, NULL);
    fclose(priv_file_sign);
    if (!priv_key) {
        std::cerr << "Error reading private key" << std::endl;
        return 1;
    }

    // Create signing context
    EVP_MD_CTX *md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) {
        std::cerr << "Error creating MD context" << std::endl;
        EVP_PKEY_free(priv_key);
        return 1;
    }

    // Initialize signing
    if (EVP_DigestSignInit(md_ctx, NULL, EVP_sha256(), NULL, priv_key) <= 0) {
        std::cerr << "Error initializing digest sign" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        EVP_PKEY_free(priv_key);
        return 1;
    }

    // Sign the message
    if (EVP_DigestSign(md_ctx, NULL, &sig_len, (unsigned char*)message.c_str(), message.length()) <= 0) {
        std::cerr << "Error determining signature length" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        EVP_PKEY_free(priv_key);
        return 1;
    }

    signature = (unsigned char*)OPENSSL_malloc(sig_len);
    if (!signature) {
        std::cerr << "Error allocating signature" << std::endl;
        EVP_MD_CTX_free(md_ctx);
        EVP_PKEY_free(priv_key);
        return 1;
    }

    if (EVP_DigestSign(md_ctx, signature, &sig_len, (unsigned char*)message.c_str(), message.length()) <= 0) {
        std::cerr << "Error signing message" << std::endl;
        OPENSSL_free(signature);
        EVP_MD_CTX_free(md_ctx);
        EVP_PKEY_free(priv_key);
        return 1;
    }

    // Save signature to file
    FILE *sig_file = fopen("signature.bin", "wb");
    if (!sig_file) {
        std::cerr << "Error opening signature file" << std::endl;
        OPENSSL_free(signature);
        EVP_MD_CTX_free(md_ctx);
        EVP_PKEY_free(priv_key);
        return 1;
    }
    fwrite(signature, 1, sig_len, sig_file);
    fclose(sig_file);

    // Clean up
    OPENSSL_free(signature);
    EVP_MD_CTX_free(md_ctx);
    EVP_PKEY_free(priv_key);

    std::cout << "Message signed and signature saved to signature.bin" << std::endl;
    return 0;
}