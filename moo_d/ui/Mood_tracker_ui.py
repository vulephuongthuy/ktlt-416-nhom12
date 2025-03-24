
import moo_d.ui.Main_Screen
from moo_d.ui.Main_Screen import *

class MoodTracker(tk.Toplevel, Base):  # Đảm bảo dùng Toplevel
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        if self.master is not None:
            self.master.mood_tracker = self
        self.title("Mood Tracker")
        self.geometry("1000x600")
        self.iconbitmap(relative_to_assets("logo.ico"))
        self.configure(bg="white")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = Canvas(self, bg="#758FC3", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.image_cache = {}
        self.load_background()
        MoodTrackerUI(self, self.canvas, self.image_cache)  # Không gọi mainloop() ở đây

    def on_close(self):
        self.destroy()  # Đóng cửa sổ
        self.quit()
        sys.exit()

    def load_background(self):
        """ Load nền và các hình ảnh """
        self.bg_image = self.load_image("mood_bg.jpg", opacity=0.6, size=(1000, 600))
        self.bg2_image = self.load_image("ffcccc.png", opacity=0.3, size=(1000, 600))
        self.button_happy_image = self.load_image("fae1fa.png", opacity=0.5, size=(333, 310))
        self.button_sad_image = self.load_image("fae1fa.png", opacity=0.5, size=(333, 310))

        self.image_cache["bg"] = self.bg_image
        self.image_cache["bg2"] = self.bg2_image
        self.image_cache["button_happy"] = self.button_happy_image
        self.image_cache["button_sad"] = self.button_sad_image

        self.canvas.create_image(500, 300, image=self.bg_image)
        self.canvas.create_image(500, 300, image=self.bg2_image)
        self.canvas.create_image(280, 320, image=self.button_happy_image, tag="btn-happy")
        self.canvas.create_image(720, 320, image=self.button_sad_image, tag="btn-sad")
        self.canvas.tag_bind("btn-happy", "<Button-1>", self.btn_happy_clicked)
        self.canvas.tag_bind("btn-sad", "<Button-1>", self.btn_sad_clicked)

    def btn_sad_clicked(self, event):
        """ Mở giao diện nghe nhạc khi chọn 'Sad' """
        self.withdraw()
        moo_d.ui.Main_Screen.MainScreen(self.master, mood="sad")

    def btn_happy_clicked(self, event):
        self.withdraw()
        moo_d.ui.Main_Screen.MainScreen(self.master)


class MoodTrackerUI(Base):
    def __init__(self, master, canvas, image_cache):
        super().__init__()
        self.master = master
        self.canvas = canvas
        self.image_cache = image_cache
        self.create_widgets()

    def create_widgets(self):
        self.canvas.create_text(500, 90, anchor="center", text="How do you feel right now?", fill="#AA60C8",
                                font=("Inter Bold", 60*-1, "bold"))

        self.canvas.create_text(210, 220, anchor="center", text="Happy", fill="#A061C5",
                                font=("Inter Bold", 35*-1, "bold"))

        self.canvas.create_text(610, 220, anchor="center", text="Sad", fill="#A061C5",font=("Inter Bold", 35*-1, "bold"))


