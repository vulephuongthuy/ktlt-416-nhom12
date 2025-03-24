import smtplib
import moo_d.session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from customtkinter import CTkEntry, CTkButton
from moo_d.ui.Mood_tracker_ui import *
from moo_d.ui.Mood_tracker_ui import MoodTracker #
from moo_d.ui.Main_Screen import Base

class LoginScreen(Base):
    def __init__(self, master = None):
        super().__init__()
        self.window = master if master else Tk()
        self.window.title("Login")
        self.window.geometry("1000x600")
        self.window.iconbitmap(relative_to_assets("logo.ico"))
        self.window.configure(bg="white")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = Canvas(self.window, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0,
                             relief="ridge")
        self.canvas.place(x=0, y=0)
        self.load_background(self.canvas)
        self.form = LoginForm(self.window, self.canvas)

    def on_close(self):
        """Thoát toàn bộ ứng dụng khi đóng LoginScreen"""
        self.window.quit()  # Dừng vòng lặp Tkinter
        self.window.destroy()
        sys.exit()

class LoginForm(Base):
    def __init__(self, master, canvas):
        super().__init__()
        self.master = master
        self.canvas = canvas

        self.username_entry = None
        self.password_entry = None
        self.signin_button = None
        self.new_window = None
        self.mood_tracker = None

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
            with open("data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "User data not found.")
            return

        for user in users:
            if user["username"] == username and user["password"] == password:
                moo_d.session.current_user = user
                self.open_moodtracker()
                return

        messagebox.showerror("Error", "Incorrect username or password!")

    def open_signup(self, event):
        self.master.withdraw()  # Ẩn màn hình đăng nhập
        self.master.after(500, self.start_signup)  # Đợi 500ms rồi mở SignUpScreen

    def start_signup(self):
        self.new_window = SignUpScreen(master=self.master)  # Truyền LoginScreen làm master

    def open_moodtracker(self):
        self.master.withdraw()  # Ẩn cửa sổ thay vì đóng hoàn toàn
        self.master.after(500, self.start_moodtracker) # Đợi 500ms trước khi mở MoodTracker

    def start_moodtracker(self):
        """Mở giao diện MoodTracker"""
        self.mood_tracker = MoodTracker(self.master)  # Truyền cửa sổ gốc vào MoodTracker

class SignUpScreen(Toplevel, Base):
    def __init__(self, master = None):
        super().__init__(master)
        Base.__init__(self)
        self.title("Sign Up")
        self.geometry("1000x600")
        self.iconbitmap(relative_to_assets("logo.ico"))
        self.configure(bg="white")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = Canvas(self, bg="#FFFFFF", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.load_background(self.canvas)
        self.form = SignUpForm(self, self.canvas)

    def on_close(self):
        """Dừng nhạc trước khi thoát ứng dụng"""
        self.destroy() # Đóng cửa sổ
        self.quit()

class SignUpForm(Base):
    def __init__(self, master, canvas):
        super().__init__()
        self.master = master
        self.canvas = canvas

        self.name_entry = None
        self.email_entry = None
        self.username_entry = None
        self.password_entry = None
        self.signup_button = None
        self.back_button = None
        self.create_widgets()

    def create_widgets(self):
        self.canvas.create_text(569.0, 37.0, anchor="nw", text="Create Account",font=("Inter Bold", 40 * -1, "bold"), fill="#F09D9D")
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
            messagebox.showerror("Error", "Please enter all fields") #
            return

        if not self.is_valid_username(username):
            messagebox.showerror("Error", "Invalid username! It must contain only letters, numbers, or underscores (_), with at least 3 characters.")
            return

        if not self.is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format! Please enter a valid email.")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return

        self.save_user(username, password, name, email)

    def save_user(self, username, password, name, email):
        try:
            with open("data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            users = []

        for user in users:
            if user["username"] == username:
                messagebox.showerror("Error", "Username already exists!")
                return
            if user["email"] == email:
                messagebox.showerror("Error", "Email is already registered!")
                return

            # Thêm người dùng mới vào danh sách
        new_user = {
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "history": [],
            "favorite_songs": [],
            "profile_picture": str(relative_to_assets("profile_default.jpg"))
        }
        users.append(new_user)

        # Lưu danh sách mới vào file JSON
        with open("data/users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Success", "User registered successfully!")
        self.go_back()
        self.send_welcome_email(email)

    @staticmethod
    def send_welcome_email(user_email):
        email_address = "thutna23416@st.uel.edu.vn"
        app_password = "wyas ubap nhqv wwap"

        msg = MIMEMultipart()
        msg["From"] = email_address
        msg["To"] = user_email
        msg["Subject"] = "Welcome to Moo_d!"

        body = """
        Hi there,

        Thank you for signing up for Moo_d Music – your new favorite place to vibe, discover, and enjoy music that matches your mood.

        We’re thrilled to have you on board!

        Stay tuned for curated playlists, personalized mood tracks, and fresh beats tailored just for you.

        Let’s set the Moo_d together.

        Cheers,  
        The Moo_d Team
        """
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(email_address, app_password)
                server.sendmail(email_address, user_email, msg.as_string())
        except smtplib.SMTPAuthenticationError as e:
            messagebox.showerror("Lỗi", f"Không thể xác thực tài khoản Gmail. Vui lòng kiểm tra mật khẩu ứng dụng. {e}")
        except Exception as e:
            print(f"Lỗi khi gửi email đến {user_email}: {e}")
            messagebox.showerror("Error", f"Failed to send email. Please try again later. {e}")

    def go_back(self):
        self.master.destroy()
        self.master.master.deiconify()  # Hiển thị lại LoginScreen

# if __name__ == "__main__":
#     root = Tk()  # Chỉ có một Tk duy nhất
#     app = LoginScreen(master=root)
#     root.mainloop()