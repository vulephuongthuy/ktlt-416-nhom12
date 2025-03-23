import json
import os
import shutil
from pathlib import Path
from tkinter import *
from tkinter import messagebox, filedialog

from PIL import Image, ImageTk
from customtkinter import CTkEntry

import moo_d.session
from moo_d.functions import *

class Profile(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Demo")
        self.geometry("600x550")
        self.resizable(False, False)
        self.iconbitmap(r"D:\HKII_NAM2\KTLT\ktlt-416-nhom12\moo_d\assets\frame0\logo.ico")

        self.canvas = Canvas(self, width=800, height=600)
        self.canvas.place(x=0, y=0)

        # Load ảnh nền
        self.background = PhotoImage(file=relative_to_assets("background.png"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.background)

        # Hiển thị ảnh Profile (mặc định nếu chưa có ảnh)
        self.profile_path = moo_d.session.current_user.get("profile_picture")

        # Nếu không có ảnh profile hoặc ảnh không tồn tại, dùng ảnh mặc định
        if not self.profile_path or not isinstance(self.profile_path, str) or not Path(self.profile_path).exists():
            self.profile_path = str(relative_to_assets("profile_default.jpg"))  # Sử dụng ảnh mặc định

        self.load_profile_image(self.profile_path)  # Hiển thị ảnh lên giao diện

        # Nút thay đổi ảnh profile
        self.change_photo_button = Button(
            self,
            text="Change pic",
            command=self.change_profile_picture,
            relief="flat",
            bg="#A352D9",
            fg="white",
            font=("Inter Bold", 14)
        )
        self.change_photo_button.place(x=25, y=190, width=110, height=30)

        self.canvas.create_text(215, 25, text="Profile", font=("Inter Bold", 45, "bold"), fill="white", anchor=NW)
        self.canvas.create_text(25, 236, text="E-mail:", font=("Inter Bold", 23), fill="#A352D9", anchor=NW)
        self.canvas.create_text(25, 306, text="Username:", font=("Inter Bold", 23), fill="#A352D9", anchor=NW)
        self.canvas.create_text(25, 376, text="Password:", font=("Inter Bold", 23), fill="#A352D9", anchor=NW)

        # Load ảnh nút Update
        self.update_button_image = PhotoImage(file=relative_to_assets("btn_update.png"))
        self.update_button = Button(
            self,
            image=self.update_button_image,
            command=self.update_info,
            relief="flat"
        )
        self.update_button.place(x=130.0, y=470.0, width=332.0, height=52.0)
        # User input
        user = moo_d.session.current_user or {}

        name = user.get("name","")
        email = user.get("email", "N/A")
        username = user.get("username", "Unknown")
        password = user.get("password", "******")

        self.name_entry = CTkEntry(self, font=("Inter", 20), fg_color="white", width=390, height=30, border_width=0,
                                   corner_radius=0, text_color="#1E1E1E")
        self.name_entry.insert(0, name)
        self.name_entry.place(x=180, y=150)

        self.canvas.create_text(265, 255, text=email, font=("Inter", 18), fill="#1E1E1E", anchor=W)

        self.username_entry = CTkEntry(self, font=("Inter", 20), fg_color="white", width=390, height=30, border_width=0,
                                       corner_radius=0, text_color="#1E1E1E")
        self.username_entry.insert(0, username)
        self.username_entry.place(x=180, y=310)

        self.password_entry = CTkEntry(self, font=("Inter", 20), fg_color="white", width=390, height=30, border_width=0,
                                       corner_radius=0, show="*", text_color="#1E1E1E")
        self.password_entry.insert(0, password)
        self.password_entry.place(x=180, y=380)

    def update_info(self):
        """Cập nhật thông tin người dùng và lưu vào file JSON"""
        user = moo_d.session.current_user or {}
        new_name = self.name_entry.get().strip()
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()
        email = user.get("email", "N/A") # Lấy email cũ để dò

        if not new_username or not new_password:
            messagebox.showerror("Error", "Please enter all fields!")
            return

        try:
            # Đọc dữ liệu từ users.json
            with open("data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)

            user_found = False
            for user in users:
                if user["email"] == email:  # Dò theo email thay vì username
                    user["name"] = new_name
                    user["username"] = new_username
                    user["password"] = new_password
                    moo_d.session.current_user = user  # Cập nhật lại thông tin trong session
                    user_found = True
                    break

            if not user_found:
                messagebox.showerror("Error", "Account not found!")
                return

            # Ghi đè dữ liệu mới vào file JSON
            with open("data/users.json", "w", encoding="utf-8") as file:
                json.dump(users, file, indent=4, ensure_ascii=False)
                file.flush()

            messagebox.showinfo("Success", "Information has been updated!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def load_profile_image(self, path):
        """Tải ảnh profile từ đường dẫn và hiển thị trên canvas"""
        try:
            # Kiểm tra xem ảnh có tồn tại không
            if not Path(path).exists():
                path = str(relative_to_assets("profile_default.png"))  # Fallback về ảnh mặc định

            img = Image.open(path)
            img = img.resize((110, 110))  # Resize ảnh profile
            self.profile_photo = ImageTk.PhotoImage(img)

            # Xóa ảnh cũ trước khi thêm ảnh mới
            self.canvas.delete("profile_pic")
            self.canvas.create_image(24, 91, anchor=NW, image=self.profile_photo, tags="profile_pic")

        except Exception as e:
            # Nếu có lỗi khi tải ảnh, fallback về ảnh mặc định
            messagebox.showwarning("Warning", f"Failed to load profile picture, using default image. Error: {e}")
            self.load_profile_image(str(relative_to_assets("profile_default.png")))

    # def change_profile_picture(self):
    #     """Mở hộp thoại chọn ảnh và cập nhật ảnh profile"""
    #     file_path = filedialog.askopenfilename(
    #         title="Chọn ảnh",
    #         filetypes=[("Ảnh PNG", "*.png"), ("Ảnh JPG", "*.jpg"), ("Ảnh JPEG", "*.jpeg"),
    #                    ("Tất cả ảnh", "*.png;*.jpg;*.jpeg")]
    #     )
    #
    #     if file_path:
    #         # Lưu ảnh vào thư mục profile_pictures
    #         new_file_path = PROFILE_PIC_PATH / Path(file_path).name
    #         shutil.copy(file_path, new_file_path)  # Sao chép ảnh vào thư mục lưu trữ
    #
    #         # Cập nhật vào file JSON ngay lập tức
    #         self.update_user_data(str(new_file_path))
    #         self.load_profile_image(str(new_file_path))
    #         return  # Kết thúc hàm để tránh lỗi
    def change_profile_picture(self):
        """Mở hộp thoại chọn ảnh, cập nhật ảnh profile và xóa ảnh cũ."""
        file_path = filedialog.askopenfilename(
            title="Chọn ảnh",
            filetypes=[("Ảnh PNG", "*.png"), ("Ảnh JPG", "*.jpg"), ("Ảnh JPEG", "*.jpeg"),
                       ("Tất cả ảnh", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            new_file_name = f"{moo_d.session.current_user['email'].replace('@', '_').replace('.', '_')}.png"
            new_file_path = PROFILE_PIC_PATH / new_file_name

            # Xóa ảnh cũ nếu tồn tại
            old_picture = moo_d.session.current_user.get("profile_picture")
            if old_picture and old_picture != str(new_file_path) and Path(old_picture).exists():
                try:
                    os.remove(old_picture)
                except Exception as e:
                    print(f"Lỗi khi xóa ảnh cũ: {e}")

            # Sao chép ảnh mới vào thư mục profile_pictures
            shutil.copy(file_path, new_file_path)

            # Cập nhật đường dẫn ảnh mới vào file JSON
            self.update_user_data(str(new_file_path))
            self.load_profile_image(str(new_file_path))
            return

    def update_user_data(self, value):
        """Cập nhật dữ liệu của user trong file JSON"""
        try:
            json_path = "data/users.json"

            # Đọc dữ liệu từ JSON
            with open(json_path, "r", encoding="utf-8") as file:
                users = json.load(file)

            user_found = False
            for user in users:
                if user.get("email") == moo_d.session.current_user.get("email"):  # Tìm đúng user
                    user["profile_picture"] = value  # Cập nhật thông tin mới
                    moo_d.session.current_user["profile_picture"] = value  # Cập nhật session
                    user_found = True
                    break

            if user_found:
                # Ghi lại dữ liệu vào file JSON
                with open(json_path, "w", encoding="utf-8") as file:
                    json.dump(users, file, indent=4, ensure_ascii=False)

            else:
                messagebox.showerror("Error", "Account not found!")

        except json.JSONDecodeError:
            messagebox.showerror("Lỗi", "File JSON bị lỗi! Vui lòng kiểm tra lại.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
