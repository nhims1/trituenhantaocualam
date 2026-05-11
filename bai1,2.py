"""Giao diện kiểm tra SHA-256, SHA-512 từ văn bản và file bằng Tkinter."""

import hashlib
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading

DEFAULT_TEXT = "Tao là lâm"


def hash_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_sha512(data: bytes) -> str:
    return hashlib.sha512(data).hexdigest()


def format_hash_text(text: str) -> tuple[str, str]:
    data = text.encode("utf-8")
    return hash_sha256(data), hash_sha512(data)


def get_sha512_file(file_path):
    h = hashlib.sha512()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class CombinedHashApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SHA-256 & SHA-512 Hash Tool")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(padx=8, pady=8)
        self._build_ui()

    def _build_ui(self) -> None:
        # Header
        header = ttk.Label(
            self,
            text="SHA-256 & SHA-512 Hash Generator",
            font=("Segoe UI", 16, "bold")
        )
        header.pack(pady=(0, 12))

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Text Hash
        self.text_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.text_frame, text="Text Hash")
        self._build_text_tab()

        # Tab 2: File Hash
        self.file_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.file_frame, text="File Hash")
        self._build_file_tab()

    def _build_text_tab(self) -> None:
        """Build the text hashing tab"""
        main_frame = ttk.Frame(self.text_frame, padding=12)
        main_frame.pack(fill="both", expand=True)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Văn bản cần băm", padding=8)
        input_frame.pack(fill="x", padx=4, pady=4)

        self.text_input = tk.Text(input_frame, height=6, wrap="word", font=("Segoe UI", 11))
        self.text_input.pack(fill="both", padx=0, pady=0)
        self.text_input.insert("1.0", DEFAULT_TEXT)

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill="x", pady=(8, 4))

        self.show_modified = tk.BooleanVar(value=True)
        show_modified_check = ttk.Checkbutton(
            options_frame,
            text="So sánh với dữ liệu đã sửa",
            variable=self.show_modified,
            onvalue=True,
            offvalue=False
        )
        show_modified_check.pack(side="left")

        button_frame = ttk.Frame(options_frame)
        button_frame.pack(side="right")

        compute_button = ttk.Button(button_frame, text="Băm dữ liệu", command=self._on_compute_text)
        compute_button.pack(side="left", padx=(0, 8))

        clear_button = ttk.Button(button_frame, text="Xóa nội dung", command=self._on_clear_text)
        clear_button.pack(side="left")

        # Result section
        result_frame = ttk.LabelFrame(main_frame, text="Kết quả băm", padding=8)
        result_frame.pack(fill="both", expand=True, padx=4, pady=4)

        result_label = ttk.Label(
            result_frame,
            text="SHA-256 và SHA-512 sẽ xuất hiện ở đây sau khi nhấn nút 'Băm dữ liệu'.",
            wraplength=700,
            justify="left"
        )
        result_label.pack(padx=0, pady=8, anchor="w")

        self.sha256_label = ttk.Label(result_frame, text="SHA-256: ", wraplength=750, justify="left")
        self.sha256_label.pack(fill="x", padx=0, pady=(6, 0))

        self.sha512_label = ttk.Label(result_frame, text="SHA-512: ", wraplength=750, justify="left")
        self.sha512_label.pack(fill="x", padx=0, pady=(6, 0))

        self.modified_label = ttk.Label(result_frame, text="", wraplength=750, justify="left", foreground="#555555")
        self.modified_label.pack(fill="x", padx=0, pady=(12, 0))

    def _build_file_tab(self) -> None:
        """Build the file hashing tab"""
        main_frame = ttk.Frame(self.file_frame, padding=12)
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="SHA-512 File Hash Calculator", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)

        # File selection
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill="x", pady=10)

        ttk.Label(file_frame, text="File:").pack(side=tk.LEFT, padx=(0, 5))
        self.file_label = ttk.Label(file_frame, text="tao là lâm", relief=tk.SUNKEN)
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        browse_btn = ttk.Button(file_frame, text="Browse", command=self._browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Calculate button
        calc_btn = ttk.Button(main_frame, text="Calculate SHA-512", command=self._calculate_file)
        calc_btn.pack(pady=20)

        # Result frame
        result_frame = ttk.LabelFrame(main_frame, text="Hash Result", padding=8)
        result_frame.pack(fill="both", expand=True, pady=10)

        ttk.Label(result_frame, text="Hash:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        # Scrollbar for result
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_result_text = tk.Text(result_frame, height=6, font=("Courier", 9),
                                        yscrollcommand=scrollbar.set, wrap=tk.WORD)
        self.file_result_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_result_text.yview)

        # Copy button
        copy_btn = ttk.Button(main_frame, text="Copy Result", command=self._copy_file_result)
        copy_btn.pack(pady=10)

        # Status bar
        self.file_status_label = ttk.Label(main_frame, text="Ready", foreground="gray")
        self.file_status_label.pack(anchor=tk.W)

        self.current_file = os.path.join(os.path.dirname(__file__), 'lannhi.jpg')

    # Text tab methods
    def _on_compute_text(self) -> None:
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản trước khi băm.")
            return

        sha256, sha512 = format_hash_text(text)
        self.sha256_label.config(text=f"SHA-256: {sha256}")
        self.sha512_label.config(text=f"SHA-512: {sha512}")

        if self.show_modified.get():
            modified_text = f"{text} (đã sửa)"
            sha256_mod, sha512_mod = format_hash_text(modified_text)
            self.modified_label.config(
                text=(
                    f"Dữ liệu đã sửa: {modified_text}\n"
                    f"SHA-256 (sửa): {sha256_mod}\n"
                    f"SHA-512 (sửa): {sha512_mod}"
                )
            )
        else:
            self.modified_label.config(text="")

    def _on_clear_text(self) -> None:
        self.text_input.delete("1.0", "end")
        self.sha256_label.config(text="SHA-256: ")
        self.sha512_label.config(text="SHA-512: ")
        self.modified_label.config(text="")

    # File tab methods
    def _browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            initialdir=os.path.dirname(self.current_file)
        )
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))

    def _calculate_file(self):
        if not os.path.exists(self.current_file):
            messagebox.showerror("Error", f"File not found: {self.current_file}")
            return

        self.file_status_label.config(text="Calculating...", foreground="orange")
        self.file_result_text.config(state=tk.NORMAL)
        self.file_result_text.delete(1.0, tk.END)
        self.update()

        # Run in thread to not block UI
        thread = threading.Thread(target=self._calculate_file_thread)
        thread.start()

    def _calculate_file_thread(self):
        try:
            hash_result = get_sha512_file(self.current_file)
            self.file_result_text.config(state=tk.NORMAL)
            self.file_result_text.insert(tk.END, hash_result)
            self.file_result_text.config(state=tk.DISABLED)
            self.file_status_label.config(text="✓ Hash calculated successfully", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.file_status_label.config(text="✗ Error", foreground="red")

    def _copy_file_result(self):
        result = self.file_result_text.get(1.0, tk.END).strip()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            messagebox.showinfo("Success", "Hash copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No hash to copy. Calculate first!")


if __name__ == "__main__":
    app = CombinedHashApp()
    app.mainloop()
