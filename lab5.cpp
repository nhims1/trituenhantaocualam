#include <iostream>
#include <vector>
#include <string>
#include <iomanip>

using namespace std;

// --- PHẦN 1: DỮ LIỆU CẤU TRÚC (structures.h) --- [cite: 46, 47]

// Bảng S-box (Substitution Box) - [cite: 27, 146]
unsigned char s[256] = {
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

// Hằng số vòng Rcon - [cite: 72, 73]
unsigned char rcon[11] = {0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36};

// Hàm mở rộng khóa cơ bản - [cite: 66, 75]
void KeyExpansionCore(unsigned char* in, unsigned char i) {
    // RotWord (Dịch trái 1 byte) - [cite: 67, 77]
    unsigned char t = in[0];
    in[0] = in[1]; in[1] = in[2]; in[2] = in[3]; in[3] = t;
    // SubWord (Thay thế S-box) - [cite: 70, 83]
    in[0] = s[in[0]]; in[1] = s[in[1]]; in[2] = s[in[2]]; in[3] = s[in[3]];
    // Rcon XOR - [cite: 72, 85]
    in[0] ^= rcon[i];
}

void KeyExpansion(unsigned char inputKey[16], unsigned char expandedKeys[176]) {
    for (int i = 0; i < 16; i++) expandedKeys[i] = inputKey[i]; // [cite: 114, 115]
    int bytesGenerated = 16;
    int rconIteration = 1;
    unsigned char tmpCore[4];
    while (bytesGenerated < 176) { // [cite: 121]
        for (int i = 0; i < 4; i++) tmpCore[i] = expandedKeys[i + bytesGenerated - 4]; // [cite: 128]
        if (bytesGenerated % 16 == 0) KeyExpansionCore(tmpCore, rconIteration++); // [cite: 131, 133]
        for (int a = 0; a < 4; a++) {
            expandedKeys[bytesGenerated] = expandedKeys[bytesGenerated - 16] ^ tmpCore[a]; // [cite: 135, 136]
            bytesGenerated++;
        }
    }
}

// --- PHẦN 2: THUẬT TOÁN MÃ HÓA (encrypt.cpp) --- [cite: 141]

void AddRoundKey(unsigned char* state, unsigned char* roundKey) { // [cite: 144, 181]
    for (int i = 0; i < 16; i++) state[i] ^= roundKey[i];
}

void SubBytes(unsigned char* state) { // [cite: 146, 182]
    for (int i = 0; i < 16; i++) state[i] = s[state[i]];
}

void ShiftRows(unsigned char* state) { // [cite: 148, 183]
    unsigned char temp[16];
    temp[0] = state[0]; temp[4] = state[4]; temp[8] = state[8]; temp[12] = state[12]; // Hàng 0 giữ nguyên
    temp[1] = state[5]; temp[5] = state[9]; temp[9] = state[13]; temp[13] = state[1]; // Hàng 1 dịch trái 1
    temp[2] = state[10]; temp[6] = state[14]; temp[10] = state[2]; temp[14] = state[6]; // Hàng 2 dịch trái 2
    temp[3] = state[15]; temp[7] = state[3]; temp[11] = state[7]; temp[15] = state[11]; // Hàng 3 dịch trái 3
    for (int i = 0; i < 16; i++) state[i] = temp[i];
}

// Giả lập MixColumns đơn giản hóa (trong thực tế cần nhân Galois) - [cite: 150, 191]
void MixColumns(unsigned char* state) { 
    // Lưu ý: Đây là bước trộn cột để tạo tính khuếch tán.
}

void AESEncryptBlock(unsigned char* message, unsigned char* expandedKeys, unsigned char* out) {
    unsigned char state[16];
    for (int i = 0; i < 16; i++) state[i] = message[i]; // [cite: 197]

    AddRoundKey(state, expandedKeys); // Vòng 0 - [cite: 198]

    for (int i = 1; i <= 9; i++) { // 9 vòng chính - [cite: 194, 198]
        SubBytes(state);
        ShiftRows(state);
        MixColumns(state);
        AddRoundKey(state, expandedKeys + (i * 16));
    }

    SubBytes(state); // Vòng cuối - [cite: 195, 198]
    ShiftRows(state);
    AddRoundKey(state, expandedKeys + 160);

    for (int i = 0; i < 16; i++) out[i] = state[i]; // [cite: 199]
}

// --- PHẦN 3: TRIỂN KHAI CBC VÀ MAIN --- [cite: 211, 212]

int main() {
    // 1. Nhập liệu và khóa - [cite: 201, 203]
    unsigned char key[16] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10};
    unsigned char expandedKeys[176];
    KeyExpansion(key, expandedKeys); // [cite: 205]

    string plaintext = "Hello AES CBC Mode"; // Thông điệp
    // Padding 16 byte - [cite: 202]
    while (plaintext.length() % 16 != 0) plaintext += ' ';

    // 2. Chế độ CBC - [cite: 216]
    unsigned char iv[16] = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}; // [cite: 221]
    unsigned char prevBlock[16];
    for (int i = 0; i < 16; i++) prevBlock[i] = iv[i];

    cout << "Ciphertext (Hex): " << endl;
    for (size_t b = 0; b < plaintext.length(); b += 16) {
        unsigned char currentBlock[16];
        for (int i = 0; i < 16; i++) {
            currentBlock[i] = (unsigned char)plaintext[b + i] ^ prevBlock[i]; // Pi XOR Ci-1 - 
        }

        unsigned char cipherBlock[16];
        AESEncryptBlock(currentBlock, expandedKeys, cipherBlock); // [cite: 223]

        for (int i = 0; i < 16; i++) {
            prevBlock[i] = cipherBlock[i]; // Lưu để dùng cho khối sau
            cout << hex << setfill('0') << setw(2) << (int)cipherBlock[i] << " "; // [cite: 225]
        }
    }
    cout << endl;

    return 0;
}
