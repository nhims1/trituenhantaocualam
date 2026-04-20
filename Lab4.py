import socket
import tkinter as tk
from tkinter import messagebox

# Thuật toán Feistel thủ công
def function_f(data_block, key):
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data_block))

def feistel_encrypt(plaintext, key):
    if len(plaintext) % 2 != 0: plaintext += " "
    mid = len(plaintext) // 2
    L_0, R_0 = plaintext[:mid], plaintext[mid:]
    f_result = function_f(R_0, key)
    R_1 = "".join(chr(ord(L_0[i]) ^ ord(f_result[i])) for i in range(len(L_0)))
    return R_1 + R_0

def send_message():
    ip = entry_ip.get()
    msg = entry_msg.get()
    key = "SECRET"
    
    if not ip or not msg:
        messagebox.showwarning("Chú ý", "Vui lòng nhập đầy đủ IP và tin nhắn!")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, 12345))
        
        ciphertext = feistel_encrypt(msg, key)
        client_socket.send(ciphertext.encode('utf-8'))
        
        lbl_status.config(text=f"Đã gửi: {ciphertext}", fg="blue")
        entry_msg.delete(0, tk.END)
        client_socket.close()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không kết nối được tới Trang: {e}")

# Tạo giao diện
window = tk.Tk()
window.title("LAB 3 - MÁY HUY (CLIENT)")
window.geometry("400x300")

tk.Label(window, text="GỬI VÀ MÃ HÓA FEISTEL", font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(window, text="Nhập IPv4 của Trang:").pack()
entry_ip = tk.Entry(window, width=30)
entry_ip.insert(0, "172.20.10.4") # Gợi ý IP
entry_ip.pack(pady=5)

tk.Label(window, text="Nhập tin nhắn:").pack()
entry_msg = tk.Entry(window, width=40)
entry_msg.pack(pady=5)

btn_send = tk.Button(window, text="Mã hóa & Gửi đi", command=send_message, bg="lightgreen", font=("Arial", 10, "bold"))
btn_send.pack(pady=20)

lbl_status = tk.Label(window, text="Trạng thái: Chờ...", fg="gray")
lbl_status.pack()

window.mainloop()