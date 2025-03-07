import json
from pathlib import Path
from tkinter import *
from tkinter import messagebox

from PIL import Image, ImageTk
from customtkinter import CTkEntry

import session

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"F:\Final\demo\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class Profile(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Demo")
        self.geometry("600x550")
        self.iconbitmap(r"F:\Final\demo\assets\frame0\logo.ico")






        self.canvas = Canvas(self, width=800, height=600)
        self.canvas.place(x=0, y=0)

        # Load ảnh nền
        self.background = PhotoImage(file=relative_to_assets("background.png"))
        self.canvas.create_image(0, 0, anchor=NW, image=self.background)

        # Load ảnh Profile
        self.profile= PhotoImage(file=relative_to_assets("profile.png"))
        self.canvas.create_image(24, 91, anchor=NW, image=self.profile)


        self.canvas.create_text(230, 25, text="Profile", font=("Inter", 35), fill="white", anchor=NW)
        self.canvas.create_text(25, 236, text="E-mail", font=("Jua", 25), fill="#A352D9", anchor=NW)
        self.canvas.create_text(25, 306, text="Username", font=("Jua", 25), fill="#A352D9", anchor=NW)
        self.canvas.create_text(25, 376, text="Password", font=("Jua", 25), fill="#A352D9", anchor=NW)

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
        user = session.current_user or {}

        name = user.get("name","")
        email = user.get("email", "N/A")
        username = user.get("username", "Unknown")
        password = user.get("password", "******")

        self.name_entry = CTkEntry(self, font=("Jua", 18), fg_color="white", width=390, height=30, border_width=0, corner_radius=0)
        self.name_entry.insert(0, name)
        self.name_entry.place(x=180, y=150)

        self.canvas.create_text(265, 255, text=email, font=("Jua", 18), fill="black")

        # self.email_entry = CTkEntry(self, font=("Jua", 18), fg_color="white", width=390, height=30, border_width=0, corner_radius=0)
        # self.email_entry.insert(0, email)
        # self.email_entry.place(x=180, y=240)

        self.username_entry = CTkEntry(self, font=("Jua", 18), fg_color="white", width=390, height=30, border_width=0, corner_radius=0)
        self.username_entry.insert(0, username)
        self.username_entry.place(x=180, y=310)

        self.password_entry = CTkEntry(self, font=("Jua", 18), fg_color="white", width=390, height=30, border_width=0, corner_radius=0, show="*")
        self.password_entry.insert(0, password)
        self.password_entry.place(x=180, y=380)

    def update_info(self):
        """Cập nhật thông tin người dùng và lưu vào file JSON"""
        user = session.current_user or {}
        new_name = self.name_entry.get().strip()
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()
        email = user.get("email", "N/A") # Lấy email cũ để dò

        if not new_username or not new_password:
            messagebox.showerror("Lỗi", "Không được để trống thông tin!")
            return

        try:
            # Đọc dữ liệu từ users.json
            with open("F:/Final/demo/data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)

            user_found = False
            for user in users:
                if user["email"] == email:  # Dò theo email thay vì username
                    user["name"] = new_name
                    user["username"] = new_username
                    user["password"] = new_password
                    session.current_user = user  # Cập nhật lại thông tin trong session
                    user_found = True
                    break

            if not user_found:
                messagebox.showerror("Lỗi", "Không tìm thấy tài khoản!")
                return

            # Ghi đè dữ liệu mới vào file JSON
            with open("F:/Final/demo/data/users.json", "w", encoding="utf-8") as file:
                json.dump(users, file, indent=4, ensure_ascii=False)
                file.flush()

            messagebox.showinfo("Thành công", "Thông tin đã được cập nhật!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
