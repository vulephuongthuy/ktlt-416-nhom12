from tkinter import Tk, Canvas
from PIL import Image, ImageTk
from customtkinter import CTkEntry, CTkButton
from Final.ui.functions import relative_to_assets, reduce_opacity, round_corners
import json
import SignUp_UI

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


class LoginScreen(Base):
    def __init__(self):
        super().__init__()
        self.window = Tk()
        self.window.title("Login")
        self.window.geometry("1000x600")
        self.window.configure(bg="white")
        self.window.resizable(False, False)
        self.canvas = Canvas(self.window, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0,
                             relief="ridge")
        self.canvas.place(x=0, y=0)
        self.load_background()
        self.form = LoginForm(self.window, self.canvas)
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


class LoginForm(Base):
    def __init__(self, master, canvas):
        super().__init__()
        self.master = master
        self.canvas = canvas
        self.create_widgets()

    def create_widgets(self):
        self.canvas.create_text(460, 70, anchor="nw", text="Welcome!", fill="#F09D9D", font=("Inter Bold", 50, "bold"))

        labels = ["Username:", "Password:"]
        positions = [170, 270]
        self.entries = {}

        for i, label in enumerate(labels):
            self.canvas.create_text(525, positions[i], text=label, font=("Inter", 16), fill="#F09D9D", anchor="w")
            entry = CTkEntry(self.master, width=340, height=40, font=("Inter", 16),
                             fg_color="transparent", text_color="#1E1E1E",
                             border_width=1, border_color="#7A7A7A",
                             placeholder_text=label[:-1], placeholder_text_color="#7A7A7A",
                             show="*" if "Password" in label else "", corner_radius=0)
            entry.place(x=530, y=positions[i] + 30)
            self.entries[label] = entry

        self.signin_button = CTkButton(self.master, cursor="hand2", width=340, height=40,
                                       text="Sign In", font=("Inter", 18), text_color="#FFFFFF",
                                       fg_color="#C6B2EA", hover_color="#6465B2", corner_radius=0,
                                       command=self.attempt_login)
        self.signin_button.place(x=530, y=370)

        self.canvas.create_text(580, 440, text="Don't have an account?", font=("Inter", 12), fill="#1E1E1E", anchor="w")
        self.canvas.create_text(750, 430, text="Sign up", font=("Inter", 12), fill="#6C4396", anchor="nw",
                                tags="signup")
        self.canvas.tag_bind("signup", "<Button-1>", self.open_signup)

    def attempt_login(self):
        username = self.entries["Username"].get()
        password = self.entries["Password"].get()

        try:
            with open("users.json", "r") as file:
                users = json.load(file)
        except FileNotFoundError:
            users = {
                "Username": username,
                "Password": password
            }

        if username in users and users[username] == password:
            print("Login successful!")
        else:
            print("Invalid username or password")

    def open_signup(self, event):
        self.master.destroy()
        SignUp_UI.SignUpScreen()


if __name__ == "__main__":
    LoginScreen()
