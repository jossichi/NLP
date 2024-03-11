import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import rarfile
import pyzipper

class PasswordCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("Password Checker")

        self.file_path_label = tk.Label(master, text="Chọn file compressed:")
        self.file_path_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.browse_button = tk.Button(master, text="Chọn File", command=self.browse_file)
        self.browse_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.password_label = tk.Label(master, text="Nhập mật khẩu:")
        self.password_label.grid(row=2, column=0, pady=5)

        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        self.check_button = tk.Button(master, text="Kiểm tra mật khẩu", command=self.check_password)
        self.check_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.result_label = tk.Label(master, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("RAR files", "*.rar"), ("ZIP files", "*.zip")])
        if file_path:
            self.file_path_label.config(text=f"File được chọn: {file_path}")
            self.file_path = file_path

            # Tự động tạo label xuất ra với thông tin về định dạng file
            file_format = "RAR" if file_path.endswith('.rar') else "ZIP"
            self.file_format_label = tk.Label(self.master, text=f"Định dạng file: {file_format}")
            self.file_format_label.grid(row=5, column=0, columnspan=2, pady=5)

            # Hiển thị thông tin về nội dung và dung lượng file nén
            self.display_compressed_file_info(file_path)
    
    def display_compressed_file_info(self, file_path):
        try:
            if file_path.endswith('.rar'):
                with rarfile.RarFile(file_path, 'r') as rar_file:
                    file_list = rar_file.namelist()
                    compressed_size = rar_file.infolist()[0].compress_size
                    password_protected = rar_file.needs_password()

            else:
                with pyzipper.AESZipFile(file_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    compressed_size = zip_file.infolist()[0].compress_size
                    password_protected = zip_file.needs_password()

            # Hiển thị thông tin về nội dung, dung lượng file nén và mật khẩu
            content_info = tk.Label(self.master, text=f"Nội dung file: {', '.join(file_list)}")
            content_info.grid(row=6, column=0, columnspan=2, pady=5)

            size_info = tk.Label(self.master, text=f"Dung lượng file nén: {compressed_size} bytes")
            size_info.grid(row=7, column=0, columnspan=2, pady=5)

            password_info = tk.Label(self.master, text=f"Có mật khẩu: {'Có' if password_protected else 'Không'}")
            password_info.grid(row=8, column=0, columnspan=2, pady=5)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi đọc file nén: {str(e)}")

    def check_password(self):
        try:
            if self.file_path.endswith('.rar'):
                with rarfile.RarFile(self.file_path, 'r') as rar_file:
                    # Lấy danh sách mật khẩu từ chính file nén
                    password_list = rar_file.namelist()

                    for password in password_list:
                        try:
                            rar_file.extractall(path=".", pwd=password.encode())
                            messagebox.showinfo("Thông báo", f"Mật khẩu chính xác: {password}")
                            return
                        except rarfile.BadRarFile:
                            continue
            else:
                with pyzipper.AESZipFile(self.file_path, 'r') as zip_file:
                    password_list = zip_file.namelist()

                    for password in password_list:
                        try:
                            zip_file.extractall(path=".", pwd=password.encode())
                            messagebox.showinfo("Thông báo", f"Mật khẩu chính xác: {password}")
                            return
                        except pyzipper.BadPassword:
                            continue

            messagebox.showinfo("Thông báo", "Không tìm thấy mật khẩu chính xác trong danh sách.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi kiểm tra mật khẩu: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()
