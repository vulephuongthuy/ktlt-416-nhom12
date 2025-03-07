from tkinter import Tk, Canvas, Toplevel
from PIL import Image, ImageTk

import guidemo
from ui.functions import *
from guidemo import *

class Base:
    def __init__(self):
        self.image_cache = {}  # Lưu trữ hình ảnh tránh bị xóa

    def load_image(self, path, opacity=None, size=None, rotate=None, round_corner=None):
        try:
            img = Image.open(relative_to_assets(path))  # Mở ảnh từ đường dẫn
            if opacity is not None:
                img = reduce_opacity(img, opacity)  # Truyền img thay vì đường dẫn
            if size:
                img = img.resize(size)
            if rotate:
                img = img.rotate(rotate)
            if round_corner:
                img = round_corners(img, round_corner)
            return ImageTk.PhotoImage(img)  # Chuyển sang định dạng dùng trong Tkinter
        except FileNotFoundError:
            print(f" Không tìm thấy ảnh: {path}")
            return None


class MoodTracker(Toplevel,Base):  # ✅ Đảm bảo dùng Toplevel
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Mood Tracker")
        self.geometry("1000x600")
        self.configure(bg="white")
        self.resizable(False, False)

        self.canvas = Canvas(self, bg="#758FC3", height=600, width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        self.image_cache = {}
        self.load_background()
        MoodTrackerUI(self, self.canvas, self.image_cache)  # ✅ Không gọi mainloop() ở đây



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
        # """ Load nền và các hình ảnh """
        # self.image_cache["bg"] = self.load_image("mood_bg.jpg", opacity=0.6, size=(1000, 600))
        # self.image_cache["bg2"] = self.load_image("ffcccc.png", opacity=0.3, size=(1000, 600))
        # self.image_cache["button_happy"] = self.load_image("fae1fa.png", opacity=0.5, size=(333, 310))
        # self.image_cache["button_sad"] = self.load_image("fae1fa.png", opacity=0.5, size=(333, 310))
        #
        # # Hiển thị hình ảnh trên Canvas
        # self.canvas.create_image(500, 300, image=self.image_cache["bg"])
        # self.canvas.create_image(500, 300, image=self.image_cache["bg2"])
        # self.canvas.create_image(280, 320, image=self.image_cache["button_happy"],tag = "btn-happy")
        # self.canvas.create_image(720, 320, image=self.image_cache["button_sad"], tag = "btn-sad")
        # self.canvas.tag_bind("btn-happy", "<Button-1>", self.btn_happy_clicked)
        # self.canvas.tag_bind("btn-sad", "<Button-1>", self.btn_sad_clicked)

    def btn_sad_clicked(self, event):
        """ Mở giao diện nghe nhạc khi chọn 'Sad' """
        self.withdraw()
        guidemo.MainScreen(mood="sad")

        guidemo.MainScreen()


    def btn_happy_clicked(self, event):
        self.withdraw()
        guidemo.MainScreen()


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


 
if __name__ == "__main__":
    MoodTracker()
