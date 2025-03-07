from tkinter import messagebox
from customtkinter import CTkEntry, CTkButton
from ui.Login_Window import Mood_tracker_ui
from ui.Login_Window.Mood_tracker_ui import *
from ui.functions import relative_to_assets, reduce_opacity, round_corners
import json
import SignUp_UI
import session

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
        self.canvas.create_text(525, 170, text="Username:", font=("Inter", 16), fill="#F09D9D", anchor="w")
        self.canvas.create_text(525, 270, text="Password:", font=("Inter", 16), fill="#F09D9D", anchor="w")


        # Entry cho Username và Password
        self.username_entry = CTkEntry(
            master=self.master,
            width=340,
            height=40,
            font=("Inter", 16),
            fg_color="transparent",
            text_color="#1E1E1E",
            border_width=1,
            border_color="#7A7A7A",
            placeholder_text="Username",
            placeholder_text_color="#7A7A7A",
            corner_radius=0
        )
        self.username_entry.place(x=530, y=200)

        self.password_entry = CTkEntry(
            master=self.master,
            width=340,
            height=40,
            font=("Inter", 16),
            fg_color="transparent",
            text_color="#1E1E1E",
            border_width=1,
            border_color="#7A7A7A",
            placeholder_text="Password",
            placeholder_text_color="#7A7A7A",
            show="*",
            corner_radius=0
        )
        self.password_entry.place(x=530, y=300)

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
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            with open("../../data/users.json", "r") as file:
                users = json.load(file)
        except FileNotFoundError:
            print("Chưa có Info người dùng. Vui lòng đăng kí")
            return

        for user in users:
            if user["username"] == username and user["password"] == password:
                session.current_user = user
                self.open_moodtracker()
                print(session.current_user)# Mở giao diện tiếp theo
                return

        messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def open_signup(self, event):
        self.master.withdraw()  # Ẩn màn hình đăng nhập
        self.master.after(500, self.start_signup)  # Đợi 500ms rồi mở SignUpScreen

    def start_signup(self):
        from ui.Login_Window.SignUp_UI import SignUpScreen
        self.new_window = SignUpScreen(master=self.master)  # ✅ Truyền LoginScreen làm master

    def open_moodtracker(self):
        print("🔹 Chuyển sang MoodTracker...")
        self.master.withdraw()  # ✅ Ẩn cửa sổ thay vì đóng hoàn toàn
        self.master.after(500, self.start_moodtracker)  # ✅ Đợi 500ms trước khi mở MoodTracker

    def start_moodtracker(self):
        """Mở giao diện MoodTracker"""
        from ui.Login_Window.Mood_tracker_ui import MoodTracker  # ✅ Import ở đây để tránh lỗi vòng lặp import
        self.new_window = MoodTracker(self.master)  # ✅ Truyền cửa sổ gốc vào MoodTracker

class SignUpScreen(Toplevel, Base):
    def __init__(self, master=None):
        super().__init__(master)
        Base.__init__(self)
        self.title("Sign Up")
        self.geometry("1000x600")
        self.configure(bg="white")
        self.resizable(False, False)
        self.canvas = Canvas(self, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.load_background()
        self.form = SignUpForm(self, self.canvas)

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
                                font=("Inter Bold", 40 * -1, "bold"))
        self.canvas.create_text(530, 100, anchor="nw", text="Name:", font=("Inter", 16), fill="#F09D9D")
        self.canvas.create_text(530, 195, anchor="nw", text="Email:", font=("Inter", 16), fill="#F09D9D")
        self.canvas.create_text(530, 288, anchor="nw", text="Username:", font=("Inter", 16), fill="#F09D9D")
        self.canvas.create_text(530, 383, anchor="nw", text="Password:", font=("Inter", 16), fill="#F09D9D")

        self.name_entry = CTkEntry(master=self.master, width=360, height=45, font=("Inter", 16), fg_color="transparent", text_color="#1E1E1E", border_width=1, border_color="#7A7A7A", placeholder_text="Enter Your Name", placeholder_text_color="#7A7A7A", corner_radius=0)
        self.name_entry.place(x=530, y=139)

        self.email_entry = CTkEntry(master=self.master, width=360, height=45, font=("Inter", 16), fg_color="transparent", text_color="#1E1E1E", border_width=1, border_color="#7A7A7A", placeholder_text="Enter Your Email", placeholder_text_color="#7A7A7A", corner_radius=0)
        self.email_entry.place(x=530, y=232)

        self.username_entry = CTkEntry(master=self.master, width=360, height=45, font=("Inter", 16), fg_color="transparent", text_color="#1E1E1E", border_width=1, border_color="#7A7A7A", placeholder_text="Choose A Username", placeholder_text_color="#7A7A7A", corner_radius=0)
        self.username_entry.place(x=530, y=325)

        self.password_entry = CTkEntry(master=self.master, width=360, height=45, font=("Inter", 16), fg_color="transparent", text_color="#1E1E1E", border_width=1, border_color="#7A7A7A", placeholder_text="Enter Your Password", placeholder_text_color="#7A7A7A", show="*", corner_radius=0)
        self.password_entry.place(x=530, y=419)

        self.signup_button = CTkButton(self.master, cursor="hand2", width=360, height=45, text="Sign Up", font=("Inter", 18), text_color="#FFFFFF", fg_color="#C6B2EA", hover_color="#6465B2", corner_radius=0, command=self.sign_up)
        self.signup_button.place(x=525, y=490)

        self.back_button = CTkButton(self.master, cursor="hand2", width=100, height=35, text="Back", font=("Inter", 16), text_color="#FFFFFF", fg_color="#C6B2EA", hover_color="#6465B2", corner_radius=0, command=self.go_back)
        self.back_button.place(x=50, y=50)

    def sign_up(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not name or not email or not username or not password:
            print("Vui lòng điền đầy đủ thông tin!")
            return

        self.save_user(username, password, name, email)

    def save_user(self, username, password, name, email):
        try:
            with open("../../data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for user in users:
            if user["username"] == username:
                print("Tên đăng nhập đã tồn tại!")
                return
            if user["email"] == email:
                print("Email đã được đăng ký!")
                return

            # Thêm người dùng mới vào danh sách
        new_user = {
            "name": name,
            "email": email,
            "username": username,
            "password": password
        }
        users.append(new_user)  # ✅ Thêm user vào danh sách

        # Lưu danh sách mới vào file JSON
        with open("../../data/users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        print("User registered successfully!")
        self.go_back()

    def go_back(self):
        self.master.destroy()
        self.master.master.deiconify()  # ✅ Hiển thị lại LoginScreen

if __name__ == "__main__":
    LoginScreen()
