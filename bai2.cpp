#include <iostream>
#include <fstream>
#include <string>
#include <openssl/rsa.h>
#include <openssl/pem.h>
#include <openssl/sha.h>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <cstring>

using namespace std;

// Function to read file content
string readFile(const string& filename) {
    ifstream file(filename, ios::binary);
    if (!file.is_open()) {
        cerr << "Error: Cannot open file " << filename << endl;
        return "";
    }
    
    string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    file.close();
    return content;
}

// Function to write binary file
bool writeFile(const string& filename, const unsigned char* data, int length) {
    ofstream file(filename, ios::binary);
    if (!file.is_open()) {
        cerr << "Error: Cannot create file " << filename << endl;
        return false;
    }
    
    file.write(reinterpret_cast<const char*>(data), length);
    file.close();
    return true;
}

// Function to load RSA private key from PEM file
RSA* loadPrivateKey(const string& keyFile) {
    FILE* fp = fopen(keyFile.c_str(), "r");
    if (!fp) {
        cerr << "Error: Cannot open key file " << keyFile << endl;
        return nullptr;
    }
    
    RSA* rsa = PEM_read_RSAPrivateKey(fp, nullptr, nullptr, nullptr);
    fclose(fp);
    
    if (!rsa) {
        cerr << "Error: Cannot read RSA private key" << endl;
        ERR_print_errors_fp(stderr);
        return nullptr;
    }
    
    return rsa;
}

// Function to compute SHA-256 hash
unsigned char* computeSHA256(const string& message, unsigned int& digest_len) {
    unsigned char* digest = new unsigned char[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, message.c_str(), message.length());
    SHA256_Final(digest, &sha256);
    
    digest_len = SHA256_DIGEST_LENGTH;
    return digest;
}

// Function to sign message using RSA
bool signMessage(const string& messageFile, const string& keyFile, const string& signatureFile) {
    // Read message
    cout << "[*] Reading message from " << messageFile << endl;
    string message = readFile(messageFile);
    if (message.empty()) {
        return false;
    }
    cout << "[+] Message read successfully (" << message.length() << " bytes)" << endl;
    cout << "[+] Message content: " << message << endl;
    
    // Load private key
    cout << "[*] Loading private key from " << keyFile << endl;
    RSA* rsa = loadPrivateKey(keyFile);
    if (!rsa) {
        return false;
    }
    cout << "[+] Private key loaded successfully" << endl;
    
    // Compute SHA-256 hash
    cout << "[*] Computing SHA-256 hash of message..." << endl;
    unsigned int digest_len;
    unsigned char* digest = computeSHA256(message, digest_len);
    cout << "[+] SHA-256 hash computed (" << digest_len << " bytes)" << endl;
    
    // Sign the hash
    cout << "[*] Signing hash with RSA private key..." << endl;
    unsigned char* signature = new unsigned char[RSA_size(rsa)];
    unsigned int signature_len;
    
    // Use RSA_sign with SHA256
    if (RSA_sign(NID_sha256, digest, digest_len, signature, &signature_len, rsa) != 1) {
        cerr << "Error: RSA_sign failed" << endl;
        ERR_print_errors_fp(stderr);
        delete[] digest;
        delete[] signature;
        RSA_free(rsa);
        return false;
    }
    cout << "[+] Message signed successfully (" << signature_len << " bytes)" << endl;
    
    // Save signature to file
    cout << "[*] Saving signature to " << signatureFile << endl;
    if (!writeFile(signatureFile, signature, signature_len)) {
        delete[] digest;
        delete[] signature;
        RSA_free(rsa);
        return false;
    }
    cout << "[+] Signature saved successfully" << endl;
    
    // Print signature in hex format
    cout << "\n[+] Signature (hex): ";
    for (unsigned int i = 0; i < signature_len; i++) {
        printf("%02x", signature[i]);
    }
    cout << "\n" << endl;
    
    // Cleanup
    delete[] digest;
    delete[] signature;
    RSA_free(rsa);
    
    return true;
}

int main() {
    // Initialize OpenSSL
    ERR_load_crypto_strings();
    OpenSSL_add_all_algorithms();
    
    cout << "========================================" << endl;
    cout << "  RSA Digital Signature (SHA-256)" << endl;
    cout << "  Buoi 6 - Bai 2" << endl;
    cout << "========================================\n" << endl;
    
    string messageFile = "message.txt";
    string keyFile = "private_key.pem";
    string signatureFile = "signature.bin";
    
    cout << "[*] Configuration:" << endl;
    cout << "    Message file: " << messageFile << endl;
    cout << "    Private key file: " << keyFile << endl;
    cout << "    Signature output: " << signatureFile << endl << endl;
    
    // Sign the message
    if (signMessage(messageFile, keyFile, signatureFile)) {
        cout << "[SUCCESS] Message signed and signature saved!" << endl;
        return 0;
    } else {
        cout << "[ERROR] Failed to sign message!" << endl;
        return 1;
    }
}
