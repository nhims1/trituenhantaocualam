import hashlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

def calculate_file_hash(file_path):
    """Tính toán mã SHA-256 của một file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Đọc file theo từng khối để tránh tốn RAM với file lớn
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

class FileTransferApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Transfer Integrity Verification")
        self.geometry("700x600")
        self.resizable(True, True)
        self.configure(padx=12, pady=12)
        
        self.source_file = None
        self.destination_file = "receiver_data.txt"
        self.sender_hash = None
        self.receiver_hash = None
        
        self._build_ui()
    
    def _build_ui(self):
        # Header
        header = ttk.Label(self, text="File Transfer Integrity Verification", 
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(0, 12))
        
        # File selection frame
        file_frame = ttk.LabelFrame(self, text="1. Chọn File để Gửi", padding=10)
        file_frame.pack(fill="x", padx=4, pady=4)
        
        file_input_frame = ttk.Frame(file_frame)
        file_input_frame.pack(fill="x", pady=8)
        
        ttk.Label(file_input_frame, text="File:").pack(side=tk.LEFT)
        self.file_label = tk.Label(file_input_frame, text="(chưa chọn file)", 
                                    relief=tk.SUNKEN, foreground="gray", padx=5)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(file_input_frame, text="Browse", command=self._browse_file).pack(side=tk.RIGHT, padx=2)
        ttk.Button(file_input_frame, text="Create Test File", 
                  command=self._create_test_file).pack(side=tk.RIGHT, padx=2)
        
        # Or create new file
        create_frame = ttk.Frame(file_frame)
        create_frame.pack(fill="x", pady=8)
        
        ttk.Label(create_frame, text="Hoặc nhập tên file mới:").pack(side=tk.LEFT)
        self.new_file_entry = ttk.Entry(create_frame)
        self.new_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(create_frame, text="Tạo File", 
                  command=self._create_custom_file).pack(side=tk.RIGHT, padx=2)
        
        # Sender side
        sender_frame = ttk.LabelFrame(self, text="2. Bên Gửi (Sender)", padding=10)
        sender_frame.pack(fill="x", padx=4, pady=4)
        
        ttk.Label(sender_frame, text="File name:").pack(anchor=tk.W)
        self.sender_file_label = tk.Label(sender_frame, text="-", 
                                           relief=tk.SUNKEN, foreground="blue", padx=5)
        self.sender_file_label.pack(fill="x", pady=4)
        
        ttk.Label(sender_frame, text="SHA-256 Hash:").pack(anchor=tk.W)
        self.sender_hash_label = tk.Label(sender_frame, text="-", 
                                           relief=tk.SUNKEN, font=("Courier", 9), padx=5)
        self.sender_hash_label.pack(fill="x", pady=4)
        
        # Transfer button
        transfer_frame = ttk.Frame(self)
        transfer_frame.pack(fill="x", pady=10)
        
        ttk.Button(transfer_frame, text="3. Simulate File Transfer", 
                  command=self._simulate_transfer).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        # Receiver side
        receiver_frame = ttk.LabelFrame(self, text="4. Bên Nhận (Receiver)", padding=10)
        receiver_frame.pack(fill="x", padx=4, pady=4)
        
        ttk.Label(receiver_frame, text="File name:").pack(anchor=tk.W)
        self.receiver_file_label = tk.Label(receiver_frame, text="-", 
                                            relief=tk.SUNKEN, foreground="green", padx=5)
        self.receiver_file_label.pack(fill="x", pady=4)
        
        ttk.Label(receiver_frame, text="SHA-256 Hash:").pack(anchor=tk.W)
        self.receiver_hash_label = tk.Label(receiver_frame, text="-", 
                                            relief=tk.SUNKEN, font=("Courier", 9), padx=5)
        self.receiver_hash_label.pack(fill="x", pady=4)
        
        # Verification result
        result_frame = ttk.LabelFrame(self, text="5. Kết Quả Xác Thực", padding=10)
        result_frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        self.result_label = tk.Label(result_frame, text="Chưa xác thực", 
                                     font=("Segoe UI", 11, "bold"), 
                                     foreground="gray", justify=tk.CENTER, wraplength=650)
        self.result_label.pack(fill="both", expand=True)
        
        # Status bar
        self.status_label = ttk.Label(self, text="Ready", foreground="gray")
        self.status_label.pack(anchor=tk.W)
    
    def _browse_file(self):
        file_path = filedialog.askopenfilename(title="Chọn file")
        if file_path:
            self.source_file = file_path
            self.file_label.config(text=os.path.basename(file_path), foreground="black")
            self._update_sender_info()
    
    def _create_test_file(self):
        self.source_file = "sender_data.txt"
        with open(self.source_file, "w", encoding="utf-8") as f:
            f.write("Dữ liệu quan trọng cần bảo mật và toàn vẹn.")
        
        self.file_label.config(text="sender_data.txt", foreground="black")
        self._update_sender_info()
        messagebox.showinfo("Success", "Test file created: sender_data.txt")
    
    def _create_custom_file(self):
        filename = self.new_file_entry.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Vui lòng nhập tên file")
            return
        
        content = filedialog.askstring("File Content", "Nhập nội dung file:")
        if content is None:
            return
        
        self.source_file = filename
        with open(self.source_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.file_label.config(text=filename, foreground="black")
        self.new_file_entry.delete(0, tk.END)
        self._update_sender_info()
        messagebox.showinfo("Success", f"File created: {filename}")
    
    def _update_sender_info(self):
        if not self.source_file or not os.path.exists(self.source_file):
            messagebox.showerror("Error", "File không tồn tại")
            return
        
        try:
            self.sender_hash = calculate_file_hash(self.source_file)
            self.sender_file_label.config(text=os.path.basename(self.source_file))
            self.sender_hash_label.config(text=self.sender_hash)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _simulate_transfer(self):
        if not self.source_file:
            messagebox.showwarning("Warning", "Vui lòng chọn file trước")
            return
        
        if not self.sender_hash:
            messagebox.showwarning("Warning", "Vui lòng tính hash của file gốc trước")
            return
        
        self.status_label.config(text="Transferring...", foreground="orange")
        self.update()
        
        thread = threading.Thread(target=self._transfer_thread)
        thread.start()
    
    def _transfer_thread(self):
        try:
            # Copy file
            with open(self.source_file, "rb") as src, open(self.destination_file, "wb") as dst:
                dst.write(src.read())
            
            # Calculate receiver hash
            self.receiver_hash = calculate_file_hash(self.destination_file)
            
            # Update UI
            self.receiver_file_label.config(text=self.destination_file)
            self.receiver_hash_label.config(text=self.receiver_hash)
            
            # Verify integrity
            if self.sender_hash == self.receiver_hash:
                self.result_label.config(
                    text="✓ KẾT QUẢ: Xác thực thành công!\nFile toàn vẹn - Không bị thay đổi",
                    foreground="green"
                )
            else:
                self.result_label.config(
                    text="✗ CẢNH BÁO: File đã bị chỉnh sửa!\nHash không khớp - Phát hiện sự thay đổi",
                    foreground="red"
                )
            
            self.status_label.config(text="✓ Transfer completed", foreground="green")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.config(text="✗ Error", foreground="red")

if __name__ == "__main__":
    app = FileTransferApp()
    app.mainloop()