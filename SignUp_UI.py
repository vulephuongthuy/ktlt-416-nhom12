from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from customtkinter import CTkEntry, CTkButton
from Final.ui.functions import relative_to_assets, reduce_opacity, round_corners
import Login_UI
import json


class Base:
    def __init__(self):
        self.image_cache = {}  # Lưu trữ hình ảnh tránh bị xóa

    def load_image(self, path, opacity=None, size=None, rotate=None, round_corner=None):
        try:
            img = Image.open(relative_to_assets(path))
            if opacity is not None:
                img = reduce_opacity(img, opacity)
            if size:
                img = img.resize(size)
            if rotate:
                img = img.rotate(rotate)
            if round_corner:
                img = round_corners(img, round_corner)
            return ImageTk.PhotoImage(img)
        except FileNotFoundError:
            print(f"Không tìm thấy ảnh: {path}")
            return None


class SignUpScreen(Base):
    def __init__(self):
        super().__init__()
        self.window = Tk()
        self.window.title("Sign Up")
        self.window.geometry("1000x600")
        self.window.configure(bg="white")
        self.window.resizable(False, False)
        self.canvas = Canvas(self.window, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0,
                             relief="ridge")
        self.canvas.place(x=0, y=0)
        self.load_background()
        self.form = SignUpForm(self.window, self.canvas)
        self.window.mainloop()

    def load_background(self):
        self.image_cache["bg"] = self.load_image("bg.jpg", opacity=0.7, size=(1020, 623))
        self.image_cache["white_box"] = self.load_image("white.jpg", opacity=0.4, size=(650, 600), round_corner=20)
        self.image_cache["note"] = self.load_image("3dnote.png", rotate=15)
        self.image_cache["heart"] = self.load_image("3dheart.png")
        self.image_cache["star"] = self.load_image("3dstar.png")
        self.image_cache["hp"] = self.load_image("3dhp.png", rotate=-20)
        self.image_cache["note2"] = self.load_image("3dnote.png", rotate=-20)
        self.canvas.create_image(500, 300, image=self.image_cache["bg"])
        self.canvas.create_image(690, 300, image=self.image_cache["white_box"])
        self.canvas.create_image(160, 200, image=self.image_cache["note"])
        self.canvas.create_image(350, 180, image=self.image_cache["heart"])
        self.canvas.create_image(130, 400, image=self.image_cache["star"])
        self.canvas.create_image(260, 330, image=self.image_cache["hp"])
        self.canvas.create_image(350, 460, image=self.image_cache["note2"])


class SignUpForm(Base):
    def __init__(self, master, canvas):
        super().__init__()
        self.master = master
        self.canvas = canvas
        self.create_widgets()

    def create_widgets(self):
        self.canvas.create_text(569.0, 37.0, anchor="nw", text="Create Account", fill="#F09D9D",
                                font=("Inter Bold", 40, "bold"))



        # # labels = ["Name:", "Email:", "Username:", "Password:"]
        # # positions = [100, 195, 288, 383]
        # # self.entries = {}
        # #
        # # for i, label in enumerate(labels):
        # #     self.canvas.create_text(530, positions[i], anchor="nw", text=label, font=("Inter", 16), fill="#F09D9D")
        # #     entry = CTkEntry(self.master, width=360, height=45, font=("Inter", 16),
        #                      fg_color="transparent", text_color="#1E1E1E",
        #                      border_width=1, border_color="#7A7A7A",
        #                      placeholder_text=f"Enter Your {label[:-1]}", placeholder_text_color="#7A7A7A",
        #                      show="*" if label == "Password:" else "", corner_radius=0)
        #     entry.place(x=530, y=positions[i] + 39)
        #     self.entries[label] = entry

        # Nút Sign Up
        self.signup_button = CTkButton(self.master, cursor="hand2", width=360, height=45,
                                       text="Sign Up", font=("Inter", 18), text_color="#FFFFFF",
                                       fg_color="#C6B2EA", hover_color="#6465B2", corner_radius=0,
                                       command=self.sign_up)
        self.signup_button.place(x=525, y=490)

        # Nút Back để quay lại màn hình Login
        self.back_button = CTkButton(self.master, cursor="hand2", width=100, height=35,
                                     text="Back", font=("Inter", 16), text_color="#FFFFFF",
                                     fg_color="#C6B2EA", hover_color="#6465B2", corner_radius=0,
                                     command=self.go_back)
        self.back_button.place(x=50, y=50)

    def sign_up(self):
        """Hàm xử lý sự kiện khi nhấn nút Sign Up"""
        name = self.entries["Name:"].get().strip()
        email = self.entries["Email:"].get().strip()
        username = self.entries["Username:"].get().strip()
        password = self.entries["Password:"].get().strip()

        if not name or not email or not username or not password:
            print("Vui lòng điền đầy đủ thông tin!")
            return

        self.save_user(username, password)

    def save_user(self, username, password):
        """Lưu thông tin người dùng vào users.json"""
        try:
            with open("users.json", "r") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = {}

        if username in users:
            print("Tài khoản đã tồn tại!")
            return

        users[username] = password

        with open("users.json", "w") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

        print("User registered successfully!")
        self.go_back()

    def go_back(self):
        """Quay lại màn hình đăng nhập"""
        self.master.destroy()
        Login_UI.LoginScreen()

if __name__ == "__main__":
    SignUpScreen()
