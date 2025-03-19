import json
import re
import threading
import time
import tkinter as tk
# from pathlib import Path

from tkinter import *
# Explicit imports to satisfy Flake8
from tkinter import Canvas, PhotoImage, Scrollbar, Scale, Frame, Label, Menu, Entry, messagebox
from tkinter.constants import VERTICAL

import pygame
# from PIL import Image, ImageDraw, ImageTk
from PIL.Image import Resampling
from mutagen.mp3 import MP3
from pygame import mixer

from demo import session
from demo.ui.functions import *
from demo.p import Profile



class Base:
    def __init__(self):
        super().__init__()
        self.image_cache = {} # Lưu trữ hình ảnh để tránh bị xóa bởi garbage collector

    def relative_to_assets(self, path):
        return str(Path(r"D:\HKII_NAM2\KTLT\ktlt-416-nhom12\demo\assets\frame0") / path)

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

    def is_valid_username(self, username):
        """Kiểm tra username chỉ chứa chữ cái, số, dấu gạch dưới (_), tối thiểu 3 ký tự."""
        return re.match(r"^[a-zA-Z0-9_]{3,}$", username) is not None

    def is_valid_email(self, email):
        """Kiểm tra định dạng email hợp lệ."""
        return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None


class MainScreen(tk.Toplevel):
    def __init__(self, mood="happy"):
        super().__init__()
        self.mood = mood
        self.resizable(False, False)
        self.title("Moo_d")
        self.iconbitmap(r"D:\HKII_NAM2\KTLT\ktlt-416-nhom12\demo\assets\frame0\logo.ico")
        self.geometry("1000x600+120+15")
        self.main_color = "#9E80AD" if self.mood == "sad" else "#E1CFE3"
        self.configure(bg="#FFFFFF")
        self.canvas = tk.Canvas(self, bg="#E1CFE3", height=600,
                                width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)
        pygame.mixer.init()
        self.buttons = Button(self, self.canvas, None)
        self.songs = Song(self, self.buttons)
        self.buttons.songs = self.songs
        self.buttons.toolbar()
        self.buttons.init_progress_bar()
        self.buttons.search_music()
        self.buttons.volume()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_colors()
        self.songs.load_user_songs()

        self.mainloop()

    def update_colors(self):
        """Cập nhật màu sắc của toàn bộ giao diện."""
        if self.mood == "sad":
            self.change_widget_colors(self)
            self.change_widget_colors(self.songs)
            self.change_widget_colors(self.buttons)

    def change_widget_colors(self, widget):
        """Duyệt tất cả widget & thuộc tính để đổi màu từ #E1CFE3 → #9E80AD"""
        if self.mood != "sad":
            return
        if isinstance(widget, (tk.Canvas, tk.Frame, tk.Label, tk.Button)):
            try:
                if widget.cget("bg") == "#E1CFE3":
                    widget.config(bg="#9E80AD")
            except tk.TclError:
                pass  # Một số widget không có bg, bỏ qua

        # Duyệt tiếp các widget con
        if hasattr(widget, "winfo_children"):
            for child in widget.winfo_children():
                self.change_widget_colors(child)

        # Nếu widget là một instance của Song, duyệt tiếp các thuộc tính nội bộ
        if isinstance(widget, (Song, Button)):
            for attr_name, attr_value in vars(widget).items():
                if isinstance(attr_value, str) and attr_value == "#E1CFE3":
                    setattr(widget, attr_name, "#9E80AD")
                elif isinstance(attr_value, tk.Widget):
                    self.change_widget_colors(
                        attr_value)  # Duyệt tiếp các widget thuộc tính

    def on_close(self):
        """Dừng nhạc trước khi thoát ứng dụng"""
        self.songs.stop_music()  # Gọi phương thức dừng nhạc từ class Song
        pygame.mixer.quit()  # Giải phóng tài nguyên pygame
        self.destroy()  # Đóng cửa sổ


class Button(Base):
    def __init__(self, parent, canvas, song):
        super().__init__()
        self.parent = parent
        self.canvas = canvas
        self.songs = song
        self.repeat_mode = 0
        self.volume_slider = None  # Biến để kiểm soát thanh volume
        self.current_volume = 100  # Mặc định 100 khi mở app
        self.is_playing = False  # Biến kiểm tra trạng thái phát nhạc
        self.is_paused = False
        self.play_button = None
        self.load_icons()
        self.parent.buttons = self
        self.progress_bg = None
        self.progress_fill = None
        self.progress_knob = None
        self.current_time_text = None  # Định nghĩa trước
        self.total_time_text = None
        self.title_text = None
        self.current_title = "Library"
        self.create_title()
        self.menu = Menu(self.parent, tearoff=0)
        self.menu.add_command(label="Profile", command=lambda: self.handle_button_press("Profile"))
        self.menu.add_command(label="Log out",command=self.logout)

    def toolbar(self):
        image_files = {
            "toolbar": ("thanh cong cu.png", 50, 300),
            "home": ("home 1.png", 50, 200),
            "heart": ("heart 1.png", 50, 271),
            "history": ("history 1.png", 50, 332),
            "setting": ("settings 1.png", 50, 393),
        }
        self.image_ids = {}
        for key, (file_name, x, y) in image_files.items():
            self.image_cache[key] = PhotoImage(
                file=self.relative_to_assets(file_name))
            img_id = self.canvas.create_image(x, y, image=self.image_cache[key])
            self.image_ids[key] = img_id

        self.canvas.tag_bind(self.image_ids["home"], "<Button-1>", lambda e: self.toggle_view("home"))
        self.canvas.tag_bind(self.image_ids["history"], "<Button-1>", lambda e: self.toggle_view("history"))
        self.canvas.tag_bind(self.image_ids["heart"], "<Button-1>", lambda e: self.toggle_view("favorites"))
        self.canvas.tag_bind(self.image_ids["setting"], "<Button-1>", lambda e: self.showMenu())
    def handle_button_press(self, btn_name):
        if btn_name == "Profile":
            Profile(self.parent)

    def showMenu(self, event=None):
        x = self.parent.winfo_pointerx()
        y = self.parent.winfo_pointery() + 50
        self.menu.post(x, y)

    def logout(self):
        """Xử lý khi bấm nút Log out"""
        try:
            # Lấy cửa sổ chính từ self.parent thay vì self
            root = self.parent.winfo_toplevel() if hasattr(self, "parent") else self.winfo_toplevel()

            # Đóng cửa sổ chính
            if isinstance(root, tk.Tk) or isinstance(root, tk.Toplevel):
                root.destroy()
            else:
                print("Không thể đóng cửa sổ chính!")
        except Exception as e:
            print(f"Lỗi khi đóng cửa sổ chính: {e}")
        self.parent.after(100, self.open_loginUI)

    def open_loginUI(self):
        """Mở lại màn hình đăng nhập"""
        from demo.ui.Login_Window.Login_UI import LoginScreen
        root = tk.Toplevel()
        login_screen = LoginScreen(master=root)

    def create_title(self):
        """Tạo hoặc cập nhật tiêu đề"""
        if self.title_text is None:
            self.title_text = self.canvas.create_text(103.0, 27.0, anchor="nw", text=self.current_title,
                                                      fill="#FFFFFF", font=("Jua Regular", 40 * -1))
        else:
            self.canvas.itemconfig(self.title_text, text=self.current_title)

    def toggle_view(self, view_type):
        """Chuyển đổi giữa danh sách bài hát, lịch sử nghe và danh sách yêu thích"""
        # Ẩn tất cả danh sách trước khi hiển thị danh sách mới
        self.hide_songs_list()
        self.hide_history()
        self.hide_favorites()

        if view_type == "home":
            self.show_songs_list()
            self.current_title = "Library"
        elif view_type == "history":
            self.show_history()
            self.current_title = "History"
        elif view_type == "favorites":
            self.show_favorites()
            self.current_title = "Favorites"
        self.create_title()

    def show_songs_list(self):
        """Hiển thị danh sách bài hát"""
        self.parent.songs.canvas.place(x=103, y=90)
        self.parent.songs.scrollbar.place(x=960, y=200, height=200)

    def hide_songs_list(self):
        """Ẩn danh sách bài hát"""
        self.parent.songs.canvas.place_forget()
        self.parent.songs.scrollbar.place_forget()

    def show_history(self):
        """Hiển thị danh sách lịch sử"""
        self.parent.songs.history_canvas.place(x=103, y=90)
        self.parent.songs.history_scrollbar.place(x=960, y=200, height=200)
        self.parent.songs.history_canvas.config(scrollregion=self.parent.songs.history_canvas.bbox("all"))

    def hide_history(self):
        """Ẩn danh sách lịch sử"""
        self.parent.songs.history_canvas.place_forget()
        self.parent.songs.history_scrollbar.place_forget()

    def show_favorites(self):
        """Hiển thị danh sách yêu thích"""
        self.parent.songs.favorites_canvas.place(x=103, y=90)
        self.parent.songs.favorites_scrollbar.place(x=960, y=200, height=200)

    def hide_favorites(self):
        """Ẩn danh sách yêu thích"""
        self.parent.songs.favorites_canvas.place_forget()
        self.parent.songs.favorites_scrollbar.place_forget()

    def init_progress_bar(self):
        """Tạo thanh tiến trình"""
        elements = {
            "progress_bg": ("rectangle", (333, 577, 864, 584), "#D9D9D9"),
            "progress_fill": ("rectangle", (333, 577, 343, 584), "#FFFFFF"),
            "progress_knob": ("oval", (333, 575, 345, 587), "#FFFFFF"),
            "current_time_text": ("text", (295, 570), "0:00"),
            "total_time_text": ("text", (873, 570), "0:00"),
        }
        for name, (shape, coords, *extra) in elements.items():
            text_color = "#FFFFFF" if self.parent.mood == "sad" else "#000000"
            if shape == "rectangle":
                setattr(self, name, self.canvas.create_rectangle(*coords, fill=extra[0], outline=""))
            elif shape == "oval":
                setattr(self, name, self.canvas.create_oval(*coords, fill=extra[0], outline=""))
            elif shape == "text":
                setattr(self, name, self.canvas.create_text(*coords, anchor="nw",
                                                            text=extra[0], fill=text_color,
                                                            font=("Newsreader Regular", -14)))

        # Gán sự kiện chuột để kéo thanh tiến trình
        self.canvas.tag_bind(self.progress_knob, "<B1-Motion>", self.seek_song)
        self.canvas.tag_bind(self.progress_fill, "<Button-1>", self.seek_song)

        self.update_progress_bar()

    def update_progress_bar(self):
        """Cập nhật thanh tiến trình"""
        if not self.songs.is_playing or self.songs.is_paused:
            return  # Không cập nhật khi đang pause
        # Lấy thời gian phát hiện tại
        current_time = self.songs.start_time + (
                pygame.mixer.music.get_pos() / 1000)
        total_time = self.songs.get_total_time()
        if current_time >= total_time:  # Nếu vượt quá thời gian bài hát thì dừng cập nhật
            current_time = total_time
        # Cập nhật giao diện
        self.canvas.itemconfig(self.current_time_text,
                               text=self.format_time(current_time))
        self.canvas.itemconfig(self.total_time_text,
                               text=self.format_time(total_time))
        # Cập nhật thanh tiến trình
        start_x, end_x = 333, 864
        progress_x = start_x + (end_x - start_x) * (current_time / total_time)
        self.canvas.coords(self.progress_fill, start_x, 577, progress_x, 584)
        self.canvas.coords(self.progress_knob, progress_x - 6, 575,
                           progress_x + 6, 587)
        # Tiếp tục cập nhật nếu nhạc đang phát
        if self.songs.is_playing and not self.songs.is_paused:
            self.canvas.after(500, self.update_progress_bar)

    def format_time(self, seconds):
        """Chuyển đổi giây sang định dạng mm:ss"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def seek_song(self, event):
        """Xử lý kéo thanh tiến trình để tua nhạc"""
        start_x, end_x = 333, 864
        total_time = self.songs.get_total_time()
        if total_time == 0:
            return
        # Tính thời gian mới
        click_x = min(max(event.x, start_x), end_x)
        new_time = ((click_x - start_x) / (end_x - start_x)) * total_time
        # Gọi class `Song` để tua bài
        self.songs.seek_song(new_time)
        self.songs.start_time = new_time  # Cập nhật start_time để không bị lệch

        self.update_progress_bar()

    def load_icons(self):
        """Tải ảnh cho các icon"""
        icons = {
            "play": "play 1.png",
            "pause": "pause 1.png",
            "previous": "previous 1.png",
            "next": "next 1.png",
            "repeat": "repeat 1.png",
            "repeat one time": "repeat one time.png",
            "repeat always": "repeat always.png",
            "love(1)": "heart (1) 1.png",
            "love(2)": "heart (2) 1.png",
            "sleeptimer": "sleeptimer.png",
        }
        for key, filename in icons.items():
            image_path = self.relative_to_assets(filename)
            if key == "sleeptimer":
                img = Image.open(image_path)
                img = img.resize((40, 40), Resampling.LANCZOS)  # Đảm bảo resize đúng
                self.image_cache[key] = ImageTk.PhotoImage(img)
            else:
                self.image_cache[key] = PhotoImage(file=image_path)
        button_positions = {
            "play": (624, 555),
            "previous": (561, 555),
            "next": (687, 555),
            "repeat": (750, 555),
            "love": (498, 559),
            "sleeptimer": (810, 555)
        }
        button_callbacks = {
            "play": self.toggle_play,
            "previous": lambda e: self.parent.songs.previous_song(e),
            "next": lambda e: self.parent.songs.next_song(e),
            "repeat": self.toggle_repeat,
            "love": self.toggle_love,
            "sleeptimer": lambda e: self.parent.songs.open_sleep_timer_window()
        }
        self.buttons = {}  # Dictionary để lưu trữ các button nếu cần dùng sau này
        self.love_state = "love(1)"
        for key, (x, y) in button_positions.items():
            image = self.image_cache[self.love_state] if key == "love" else self.image_cache[key]
            self.buttons[key] = self.canvas.create_image(x, y, image=image)
            self.canvas.tag_bind(self.buttons[key], "<Button-1>", button_callbacks[key])

    def toggle_love(self, event=None):
        """Chuyển đổi trạng thái của nút love"""
        if self.love_state == "love(1)":
            self.love_state = "love(2)"
            self.parent.songs.add_to_favorites()
        else:
            self.love_state = "love(1)"
            self.parent.songs.remove_from_favorites()
        # Cập nhật hình ảnh của nút love
        self.canvas.itemconfig(self.buttons["love"], image=self.image_cache[self.love_state])

    def toggle_play(self, event=None):
        if pygame.mixer.music.get_busy():  # Nếu đang phát nhạc
            pygame.mixer.music.pause()
            self.is_playing = False
            self.canvas.itemconfig(self.buttons["play"], image=self.image_cache["play"])
        else:  # Nếu nhạc đang tạm dừng hoặc chưa phát
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.canvas.itemconfig(self.buttons["play"], image=self.image_cache["pause"])

    def toggle_repeat(self, event=None):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        self.parent.songs.repeat_mode = self.repeat_mode  # Cập nhật repeat_mode trong Song

        if self.repeat_mode == 0:
            self.canvas.itemconfig(self.buttons["repeat"], image=self.image_cache["repeat"])
        elif self.repeat_mode == 1:
            self.canvas.itemconfig(self.buttons["repeat"], image=self.image_cache["repeat one time"])
        else:
            self.canvas.itemconfig(self.buttons["repeat"], image=self.image_cache["repeat always"])

    # Tạo khung tìm kiếm bo góc bằng ảnh
    def create_rounded_rectangle(self, width, height, radius, color):
        # Tạo ảnh hình chữ nhật bo góc
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Nền trong suốt
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((0, 0, width, height), radius=radius,
                               fill=color)
        return ImageTk.PhotoImage(img)

    def search_music(self):
        self.image_cache["search_box"] = self.create_rounded_rectangle(235, 30, 15, "#FDF4FF")
        self.canvas.create_image(851, 42, image=self.image_cache["search_box"])
        self.image_cache["search"] = PhotoImage(file=self.relative_to_assets("search 1.png"))
        self.canvas.create_image(755, 42, image=self.image_cache["search"])
        self.search_entry = Entry(self.canvas, font=("Newsreader Regular", 14),
                                  fg="#000000", bg="#FDF4FF", bd=0)
        self.search_entry.place(x=773, y=30, width=188, height=27)
        self.search_entry.bind("<Return>", self.parent.songs.search_song)

    def volume(self):
        self.image_cache["volume"] = PhotoImage(file=self.relative_to_assets("high-volume 1.png"))
        self.volume_icon = self.canvas.create_image(978, 570,
                                                    image=self.image_cache["volume"])
        # Gán sự kiện click vào icon volume
        self.canvas.tag_bind(self.volume_icon, "<Button-1>", self.toggle_volume_slider)

    def toggle_volume_slider(self, event=None):
        """Hiện hoặc ẩn thanh volume khi nhấn vào icon"""
        if self.volume_slider and self.volume_slider.winfo_ismapped():
            self.volume_slider.place_forget()  # Ẩn nếu đang hiện
        else:
            self.show_volume_slider()

    def show_volume_slider(self):
        """Hiển thị thanh điều chỉnh âm lượng với thiết kế bo tròn"""
        volume_color = "#9E80AD" if self.parent.mood == "sad" else "#E1CFE3"
        text_color = "#FFFFFF" if self.parent.mood == "sad" else "#000000"
        if not self.volume_slider:
            self.volume_slider = Scale(
                self.canvas.master, from_=100, to=0, orient=VERTICAL,
                length=100, sliderlength=20, width=10, troughcolor="#E9AFE7",
                bg=volume_color, fg=text_color,
                highlightthickness=0, borderwidth=0, command=self.set_volume
            )
        self.volume_slider.set(self.current_volume)
        self.volume_slider.place(x=950, y=450)  # Đặt vị trí gần icon volume

    def set_volume(self, value):
        """Cập nhật âm lượng của trình phát nhạc"""
        self.current_volume = int(value)  # Lưu lại mức âm lượng hiện tại
        pygame.mixer.music.set_volume(int(value) / 100)  # Giá trị từ 0.0 đến 1.0


class Song(Base):
    def __init__(self, parent, button):
        super().__init__()
        self.parent = parent
        self.history_list = []
        self.favorite_songs = []
        self.button = button
        self.is_paused = False
        self.check_end_id = None
        mixer.init()
        self.current_song = None
        self.is_playing = False
        self.repeat_mode = 0  # 0: No Repeat, 1: Repeat One, 2: Repeat Always
        self.repeat_once_flag = False

        self.current_time = 0
        self.total_time = 0
        self.paused_time = 0
        self.start_time = 0

        # Canvas lịch sử
        self.history_canvas = Canvas(self.parent, width=844, height=408, bg="#E1CFE3", bd=0, highlightthickness=0)
        self.history_canvas.place(x=103, y=90)
        self.history_canvas.place_forget()  # Ẩn ngay khi khởi tạo
        self.history_frame = Frame(self.history_canvas, bg="white")
        self.history_canvas_window = self.history_canvas.create_window((0, 0), window=self.history_frame,
                                                                       anchor="nw", width=844)
        # Tạo một canvas riêng để chứa danh sách bài hát
        self.canvas = Canvas(self.parent, width=844, height=408, bg="#E1CFE3", bd=0, highlightthickness=0)
        self.canvas.place(x=103, y=90)  # Đặt vị trí cho danh sách bài hát

        # Tạo thanh cuộn dọc cho canvas song
        self.scrollbar = Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollbar.place(x=960, y=200, height=200)  # Đặt vị trí thanh cuộn
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<MouseWheel>", self.scroll_with_mouse)

        # Tạo thanh cuộn cho history_canvas
        self.history_scrollbar = Scrollbar(self.parent, orient="vertical", command=self.history_canvas.yview)
        self.history_scrollbar.place(x=960, y=200, height=200)
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)
        self.history_scrollbar.place_forget()
        self.history_canvas.bind("<Configure>", self.update_scroll_region)
        self.parent.bind("<MouseWheel>", self.scroll_with_mouse)

        # Canvas yêu thích
        self.favorites_canvas = Canvas(self.parent, width=844, height=408, bg="#E1CFE3", bd=0, highlightthickness=0)
        self.favorites_canvas.place(x=103, y=90)
        self.favorites_canvas.place_forget()  # Ẩn ngay khi khởi tạo
        self.favorites_frame = Frame(self.favorites_canvas, bg="#E1CFE3")
        self.favorites_canvas_window = self.favorites_canvas.create_window((0, 0), window=self.favorites_frame,
                                                                           anchor="nw", width=844)

        # Tạo thanh cuộn cho history_canvas
        self.favorites_scrollbar = Scrollbar(self.parent, orient="vertical", command=self.favorites_canvas.yview)
        self.favorites_scrollbar.place(x=960, y=200, height=200)
        self.favorites_canvas.configure(yscrollcommand=self.favorites_scrollbar.set)
        self.favorites_scrollbar.place_forget()
        self.favorites_canvas.bind("<Configure>", self.update_scroll_region)
        self.parent.bind("<MouseWheel>", self.scroll_with_mouse)

        self.current_index = -1  # Chỉ mục của bài hát hiện tại
        self.songs_list = []  # Danh sách bài hát
        self.fixed_canvas = Canvas(self.parent, bg="#E1CFE3", height=78,
                                   width=266, bd=0, highlightthickness=0)
        self.fixed_canvas.place(x=0, y=522)  # Đặt ở dưới cùng

        self.load_songs()
        self.load_user_songs() # Sau khi đăng nhập tự động load history & favorite song của current user

        # Bắt sự kiện khi bài hát kết thúc
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.parent.bind("<Configure>", self.check_song_end)
        self.update_colors = self.parent.update_colors

    def load_user_songs(self):
        """Tải danh sách lịch sử và yêu thích từ users.json và lấy dữ liệu từ songs.json để hiển thị"""
        user = session.current_user
        user_history = user.get("history", [])
        user_favorites = user.get("favorite_songs", [])

        self.favorite_songs = []
        self.history_list = []

        # Thêm bài hát vào danh sách yêu thích
        for song_id in user_favorites:
            if song_id in self.song_data:  # Kiểm tra xem song_id có tồn tại trong songs_data không
                self.favorite_songs.append(self.song_data[song_id])
            else:
                print(f"Bài hát {song_id} không có trong songs.json!")

        # Thêm bài hát vào danh sách lịch sử
        for song_id in user_history:
            if song_id in self.song_data:
                self.history_list.append(self.song_data[song_id])
            else:
                print(f"Bài hát {song_id} không có trong songs.json!")

        # Cập nhật hiển thị
        self.update_favorites_display()
        self.update_history_display()


    def save_to_history(self, song_id):
        """Lưu bài hát vào lịch sử phát"""
        if song_id not in self.song_data:
            print(f"Lỗi: Không tìm thấy song_id {song_id} trong song_data")
            return

        song_file = self.songs_list[self.current_index]

        self.history_list = [entry for entry in self.history_list if entry["audio"] != song_file]
        self.history_list.insert(0, self.song_data[song_id])

        self.update_history_display()

    def update_history_display(self):
        """Cập nhật hiển thị lịch sử"""
        for widget in self.history_frame.winfo_children():
            widget.destroy()  # Xóa danh sách cũ
        for index, song in enumerate(self.history_list):
            title = song["title"]
            artist = song["artist"]
            image_file = song["image"]
            song_id = song["id"]
            self.create_history_item(100, 100 + index * 50, title, artist,
                                     image_file, song_id)
        # Cập nhật lại khung cuộn chính xác
        self.history_frame.update_idletasks()
        self.history_canvas.config(scrollregion=self.history_canvas.bbox("all"))

    def create_history_item(self, x, y, title, artist, image_file, song_id):
        """Tạo một ô bài hát trong khung lịch sử"""
        frame = Frame(self.history_frame, bg="#E1CFE3", padx=10, pady=5)
        frame.pack(fill="x", expand=True)
        img = PhotoImage(file=self.relative_to_assets(image_file))
        img_label = Label(frame, image=img, bg="#E1CFE3")
        img_label.image = img
        img_label.pack(side="left", padx=10)

        text_frame = Frame(frame, bg="#E1CFE3")
        text_frame.pack(side="left", fill="x", expand=True)

        text_color = "#FFFFFF" if self.parent.mood == "sad" else "#000000"
        title_label = Label(text_frame, text=title, font=("Coiny Regular",
                                                          18), fg=text_color, bg="#E1CFE3")
        title_label.pack(anchor="w")
        artist_label = Label(text_frame, text=artist, font=("Newsreader Regular", 14), fg=text_color, bg="#E1CFE3")
        artist_label.pack(anchor="w")
        frame.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_history(song_id))
        img_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_history(song_id))
        title_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_history(song_id))
        artist_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_history(song_id))
        self.parent.change_widget_colors(frame)

    def play_song_from_history(self, song_id):
        """Phát nhạc khi nhấn vào bài hát trong lịch sử"""
        for entry in self.history_list:
            if entry["id"] == song_id:
                index = list(self.song_data.keys()).index(song_id)
                self.play_song(index)
                self.on_song_click(song_id)
                self.save_to_history(song_id)
                return

    def scroll_history(self, *args):
        """Cuộn danh sách lịch sử khi kéo thanh cuộn"""
        self.history_canvas.yview(*args)

    def update_scroll_region(self, event=None):
        """Cập nhật kích thước vùng cuộn dựa trên nội dung"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        self.favorites_canvas.configure(scrollregion=self.favorites_canvas.bbox("all"))

    def scroll_with_mouse(self, event):
        """Cuộn danh sách bằng chuột giữa"""
        if self.history_canvas.winfo_ismapped():
            self.history_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif self.favorites_canvas.winfo_ismapped():
            self.favorites_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        else:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def update_favorite_songs(self, song_id, action=None):
        """Cập nhật danh sách favorite_songs của user hiện tại"""
        user = session.current_user or {}
        email = user.get("email")

        try:
            with open("../../data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
            for user in users:
                if user["email"] == email:
                    if action == "add":
                        if song_id not in user["favorite_songs"]:
                            user["favorite_songs"].append(song_id)  # Thêm ID bài hát
                    elif action == "remove":
                        if song_id in user["favorite_songs"]:
                            user["favorite_songs"].remove(song_id)  # Xóa ID bài hát

            with open("../../data/users.json", "w", encoding="utf-8") as file:
                json.dump(users, file, indent=4, ensure_ascii=False)
                file.flush()
                return
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


    def update_history_songs(self, song_id):
        """Cập nhật danh sách history của user hiện tại"""
        user = session.current_user or {}
        email = user.get("email")

        try:
            with open("../../data/users.json", "r", encoding="utf-8") as file:
                users = json.load(file)

            for user in users:
                if user["email"] == email:
                    # Nếu song_id đã có trong history, xóa đi trước khi thêm lại
                    if song_id in user["history"]:
                        user["history"].remove(song_id)

                    # Thêm song_id vào đầu danh sách history
                    user["history"].insert(0, song_id)

                    # Ghi lại file users.json
            with open("../../data/users.json", "w", encoding="utf-8") as file:
                json.dump(users, file, indent=4, ensure_ascii=False)
                file.flush()
                return
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")


    def add_to_favorites(self):
        """Lưu bài hát hiện tại vào danh sách yêu thích"""
        if self.current_index is None or self.current_index >= len(
                self.songs_list):
            print("Không có bài hát nào đang phát hoặc index không hợp lệ")
            return
        song_id = list(self.song_data.keys())[self.current_index]
        song_file = self.songs_list[self.current_index]

        self.favorite_songs = [entry for entry in self.favorite_songs if
                               entry["audio"] != song_file]
        self.favorite_songs.insert(0, self.song_data[song_id])

        self.update_favorite_songs(song_id, action="add")
        self.update_favorites_display()


    def update_favorites_display(self, show_ui=False):
        """Cập nhật hoặc hiển thị danh sách yêu thích"""
        if show_ui:
            self.favorites_canvas.place(x=103, y=90)  # Hiển thị danh sách yêu thích
            self.history_canvas.place_forget()  # Ẩn lịch sử
            self.canvas.place_forget()  # Ẩn danh sách bài hát chính
        # Xóa danh sách yêu thích cũ
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()
        # Tạo lại danh sách yêu thích
        for index, song in enumerate(self.favorite_songs):
            self.create_favorite_item(100, 100 + index * 50, song["title"],
                                      song["artist"], song["image"], song["id"])

        # Cập nhật khung cuộn
        self.favorites_frame.update_idletasks()
        self.favorites_canvas.config(scrollregion=self.favorites_canvas.bbox("all"))

    def remove_from_favorites(self):
        """Xóa bài hát khỏi danh sách yêu thích và cập nhật giao diện ngay lập tức"""
        if self.current_index is None:
            print("Không có bài hát nào đang phát")
            return

        song_id = list(self.song_data.keys())[self.current_index]
        self.favorite_songs = [song for song in self.favorite_songs if
                               song.get("id") != song_id]
        self.update_favorite_songs(song_id, action="remove")
        self.update_favorites_display(
            show_ui=self.parent.buttons.current_title == "Favorites")

        self.update_love_button()

    def create_favorite_item(self, x, y, title, artist, image_file, song_id):
        """Tạo một ô bài hát trong danh sách yêu thích"""
        frame = Frame(self.favorites_frame, bg="#E1CFE3", padx=10, pady=5)
        frame.pack(fill="x", expand=True)

        img = PhotoImage(file=self.relative_to_assets(image_file))
        img_label = Label(frame, image=img, bg="#E1CFE3")
        img_label.image = img
        img_label.pack(side="left", padx=10)

        text_frame = Frame(frame, bg="#E1CFE3")
        text_frame.pack(side="left", fill="x", expand=True)

        text_color = "#FFFFFF" if self.parent.mood == "sad" else "#000000"
        title_label = Label(text_frame, text=title, font=("Coiny Regular",18), fg=text_color, bg="#E1CFE3")
        title_label.pack(anchor="w")

        artist_label = Label(text_frame, text=artist, font=("Newsreader "
                                                            "Regular", 14),
                             fg=text_color, bg="#E1CFE3")
        artist_label.pack(anchor="w")

        frame.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_favorites(song_id))
        img_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_favorites(song_id))
        title_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_favorites(song_id))
        artist_label.bind("<Button-1>", lambda e, s_id=song_id: self.play_song_from_favorites(song_id))
        self.parent.change_widget_colors(frame)

    def play_song_from_favorites(self, song_id):
        """Phát nhạc khi nhấn vào bài hát trong danh sách yêu thích"""
        song = None
        for s in self.favorite_songs:
            if s["id"] == song_id:
                song = s
                break
        try:
            index = list(self.song_data.keys()).index(song_id)
            self.play_song(index)  # Phát bài hát
            self.on_song_click(song_id)  # Cập nhật giao diện
            self.add_to_favorites()  # Lưu lại vào danh sách yêu thích để cập nhật vị trí
        except ValueError:
            print(f"Lỗi: Không tìm thấy bài hát '{song['title']}' trong danh sách gốc.")

    def search_song(self, event=None):
        """Tìm kiếm bài hát theo tiêu đề hoặc ca sĩ"""
        keyword = self.parent.buttons.search_entry.get().strip().lower()

        if not keyword:
            return  # Nếu ô tìm kiếm trống, không làm gì cả
        # Tìm kiếm bài hát có tiêu đề hoặc ca sĩ khớp với keyword
        for index, (song_id, song_info) in enumerate(
                self.song_data.items()):
            title_match = keyword == song_info["title"].lower()  # So khớp toàn bộ tiêu đề
            artist_match = keyword == song_info["artist"].lower()  # So khớp toàn bộ nghệ sĩ

            if title_match or artist_match:  # Chỉ hiện nếu nhập đúng 100%
                self.on_song_click(song_id)  # Hiển thị bài hát trong khu vực cố định

                if 0 <= index < len(
                        self.songs_list):  # Kiểm tra index hợp lệ
                    self.current_index = index  # Cập nhật index bài hát hiện tại
                    song_path = self.songs_list[
                        index]  # Lấy đường dẫn bài hát

                    # Cập nhật đường dẫn vào song_data nếu chưa có
                    self.song_data[song_id]["file"] = song_path
                    # Gọi hàm phát nhạc
                    self.play_song(index)

                return

        # Nếu không tìm thấy bài hát, có thể hiển thị thông báo (tùy chọn)
        print("Không tìm thấy bài hát phù hợp!")

    def check_song_end(self, event=None):
        """Kiểm tra khi bài hát kết thúc và xử lý chế độ lặp lại"""
        try:
            # Nếu đang Pause thì KHÔNG kiểm tra
            if self.is_paused:
                return
                # Lấy tổng thời lượng bài hát
            audio = MP3(self.songs_list[self.current_index])
            song_length = audio.info.length  # Thời gian bài hát tính bằng giây
            # Lấy thời gian phát hiện tại
            current_time = self.start_time + (pygame.mixer.music.get_pos() / 1000)
            # Kiểm tra nếu bài hát thực sự đã hết (không chỉ là bị Pause)
            if current_time >= song_length - 0.5:  # Giảm sai số 0.5 giâY
                self.start_time = 0
                self.paused_time = 0

                if self.repeat_mode == 1:  # Repeat One Time (Phát lại 1 lần)
                    if not self.repeat_once_flag:
                        self.repeat_once_flag = True  # Đánh dấu đã lặp lại 1 lần
                        pygame.mixer.music.stop()
                        self.play_song(self.current_index)
                    else:
                        self.repeat_once_flag = False  # Reset flag cho lần sau
                        self.next_song()  # Chuyển bài
                elif self.repeat_mode == 2:  # Repeat Always (Lặp lại vô hạn)
                    pygame.mixer.music.stop()
                    self.play_song(self.current_index)
                else:  # Chế độ bình thường, chuyển bài tiếp theo
                    self.next_song()
            else:
                # Tiếp tục kiểm tra sau 500ms
                self.parent.after(500, self.check_song_end)

        except Exception as e:
            print("Lỗi khi đọc file nhạc:", e)

    def seek_song(self, new_time):
        """Tua bài hát đến thời gian mới"""
        pygame.mixer.music.stop()  # Dừng nhạc trước khi tua
        pygame.mixer.music.play(start=new_time)  # Phát lại từ vị trí mới
        # Cập nhật lại thời gian bắt đầu theo hệ thống
        self.start_time = time.time() - new_time
        self.paused_time = 0  # Reset thời gian pause để tránh lỗi cộng dồn
        # Cập nhật lại thanh tiến trình ngay lập tức
        self.parent.buttons.update_progress_bar()

    def get_paused_time(self):
        """Trả về thời gian tại điểm pause"""
        return self.paused_time

    def get_start_time(self):
        """Trả về thời gian bắt đầu của bài hát"""
        return self.start_time

    def get_current_time(self):
        """Lấy thời gian hiện tại của bài hát đang phát"""
        if pygame.mixer.music.get_busy():
            self.current_time = pygame.mixer.music.get_pos() / 1000  # Chuyển từ ms sang giây
        return self.current_time

    def get_total_time(self):
        """Lấy tổng thời gian bài hát hiện tại"""
        if self.current_index == -1:
            return 0
        audio = MP3(self.songs_list[self.current_index])
        return audio.info.length

    def play_song(self, index):
        """Phát bài hát theo chỉ mục"""
        if self.is_paused:
            self.pause_and_resume_song()
        elif self.songs_list and 0 <= index < len(self.songs_list):
            self.current_index = index
            song_path = self.songs_list[index]
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.start_time = 0
            self.paused_time = 0

            audio = MP3(self.songs_list[index])
            self.total_time = audio.info.length

            # Cập nhật nút Play -> Pause
            self.parent.buttons.canvas.itemconfig(
                self.parent.buttons.buttons["play"],
                image=self.parent.buttons.image_cache["pause"]
            )

            self.parent.buttons.update_progress_bar()
            # Gọi hàm cập nhật giao diện bài hát đang phát
            song_id = list(self.song_data.keys())[index]  # Lấy song_id từ danh sách
            self.on_song_click(song_id)  # Cập nhật thông tin bài hát
            self.update_history_songs(song_id)
            self.save_to_history(song_id)
            self.update_love_button()

    def update_love_button(self):
        """Cập nhật trạng thái nút love khi chuyển bài"""
        if self.current_index is None:
            return
        song_id = list(self.song_data.keys())[self.current_index]
        # Kiểm tra xem bài hát có trong danh sách yêu thích không
        is_favorite = any(song["id"] == song_id for song in self.favorite_songs)
        love_button_key = "love(2)" if is_favorite else "love(1)"
        # Cập nhật hình ảnh của nút love
        self.parent.buttons.canvas.itemconfig(
            self.parent.buttons.buttons["love"],
            image=self.parent.buttons.image_cache[love_button_key]
        )

    def pause_and_resume_song(self):
        """Tạm dừng nhạc"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            # Nếu bài hát đã kết thúc, không cập nhật start_time nữa
            if pygame.mixer.music.get_busy():
                self.start_time = time.time() - self.paused_time
            self.paused_time = 0  # Reset paused_time

            self.parent.buttons.canvas.itemconfig(
                self.parent.buttons.play_button,
                image=self.parent.buttons.image_cache["pause"]
            )
            self.parent.buttons.update_progress_bar()
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.paused_time = pygame.mixer.music.get_pos() / 1000

            self.parent.buttons.canvas.itemconfig(
                self.parent.buttons.play_button,
                image=self.parent.buttons.image_cache["play"]
            )


    def next_song(self, event=None):
        if self.songs_list:
            self.repeat_once_flag = False
            self.current_index = (self.current_index + 1) % len(self.songs_list)
            self.play_song(self.current_index)

    def previous_song(self, event=None):
        if self.songs_list:
            self.current_index = (self.current_index - 1) % len(self.songs_list)
            self.play_song(self.current_index)

    def stop_music(self):
        pygame.mixer.music.stop()

    def create_song(self, song):
        """Tạo một ô bài hát"""
        key = song["id"]
        rect_id = self.canvas.create_rectangle(song["x1"], song["y1"], song["x2"], song["y2"], fill="#FFFFFF", outline="")
        title_id = self.canvas.create_text(song["title_x"], song["title_y"], anchor="nw",
                                           text=song["title"],
                                           fill="#000000", font=("Coiny Regular", 18 * -1))
        artist_id = self.canvas.create_text(song["artist_x"], song["artist_y"], anchor="nw",
                                            text=song["artist"], fill="#000000", font=("Newsreader Regular", 14 * -1))
        self.image_cache[key] = PhotoImage(file=self.relative_to_assets(song["image"]))
        img_id = self.canvas.create_image(song["image_x"], song["image_y"], image=self.image_cache[key])
        index = len(self.songs_list)  # Lưu index hiện tại
        self.songs_list.append(song["audio"])  # Lưu bài hát vào danh sách
        # Lưu thông tin bài hát vào dictionary
        if not hasattr(self, "song_data"):
            self.song_data = {}
        self.song_data[key] = song
        self.song_data[key]["inndex"] = index
        for item_id in [rect_id, title_id, artist_id, img_id]:
            self.canvas.tag_bind(item_id, "<Button-1>", lambda e, idx=index, song_id=key: (self.play_song(idx), self.on_song_click(song_id)))


    def on_song_click(self, song_id):
        """Khi click vào bài hát, cập nhật hiển thị thông tin bài hát ở vị trí cố định"""
        if song_id not in self.song_data:
            return  # Không tìm thấy dữ liệu bài hát
        song = self.song_data[song_id]
        # Xóa nội dung cũ nếu có
        self.fixed_canvas.delete("all")
        # Load ảnh bài hát
        image_path = self.relative_to_assets(song["image"])
        pil_image = Image.open(image_path).resize((68, 68), Resampling.LANCZOS)
        self.current_song_image = ImageTk.PhotoImage(pil_image)  # Lưu để tránh bị xóa bởi garbage collector
        text_color = "#FFFFFF" if self.parent.mood == "sad" else "#000000"
        # Hiển thị ảnh, tiêu đề bài hát và tên nghệ sĩ trên `fixed_canvas`
        self.fixed_canvas.create_image(20, 5, anchor="nw", image=self.current_song_image)  # Ảnh cố định
        self.fixed_canvas.create_text(104, 27, text=song["title"], fill=text_color, font=("Coiny Regular", 18 * -1),
                                      anchor="w")
        self.fixed_canvas.create_text(104, 50, text=song["artist"], fill=text_color,
                                      font=("Newsreader Regular", 14 * -1), anchor="w")

    def load_songs(self):
        """Load danh sách bài hát từ file JSON"""
        self.songs_list = []  # Reset danh sách bài hát, chứa audio
        with open("../../data/songs.json", "r", encoding="utf-8") as file:
            songs = json.load(file)

        base = Base()

        for song in songs:
            song["audio"] = base.relative_to_assets(song["audio"])
            self.create_song(song)


    def open_sleep_timer_window(self):
        """Mở cửa sổ Sleep Timer hoặc hiện lại nếu đang ẩn"""
        if hasattr(self, "sleep_window") and self.sleep_window.winfo_exists():
            self.sleep_window.deiconify()  # Hiện lại nếu cửa sổ đã tồn tại
            return

        # Nếu chưa có cửa sổ, tạo mới
        self.sleep_window = tk.Toplevel(self.parent)
        self.sleep_window.title("Sleep Timer")
        self.sleep_window.geometry("300x200")
        self.sleep_window.configure(bg="#E1CFE3")
        self.sleep_window.resizable(False, False)

        Label(self.sleep_window, text="Hẹn giờ tắt ứng dụng:", font=("Jua", 14), bg="white").pack(pady=10)

        # Entry nhập số phút
        self.sleep_timer_entry = tk.Entry(self.sleep_window, font=("Jua", 12), width=10)
        self.sleep_timer_entry.pack(pady=5)
        self.sleep_timer_entry.insert(0, "10")  # Mặc định là 10 phút

        # Nút Bắt đầu và Hủy hẹn giờ
        start_btn = tk.Button(self.sleep_window, text="Bắt đầu", font=("Jua", 12), command=self.start_sleep_timer)
        start_btn.pack(pady=5)

        stop_btn = tk.Button(self.sleep_window, text="Hủy", font=("Jua", 12), command=self.stop_sleep_timer)
        stop_btn.pack(pady=5)

        self.sleep_timer_running = False

    def start_sleep_timer(self):
        """Bắt đầu Sleep Timer"""
        try:
            minutes = int(self.sleep_timer_entry.get())  # Lấy số phút từ user nhập
            self.sleep_time = minutes * 60  # Chuyển đổi thành giây
            self.sleep_timer_running = True
            self.sleep_window.withdraw()  # Ẩn cửa sổ thay vì hủy

            # Chạy đếm ngược trong một luồng riêng để không chặn UI
            self.sleep_thread = threading.Thread(target=self.run_sleep_timer, daemon=True)
            self.sleep_thread.start()
            messagebox.showinfo("Sleep Timer", f"Ứng dụng sẽ dừng nhạc sau {minutes} phút.")

        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập một số nguyên hợp lệ!")

    def run_sleep_timer(self):
        """Chạy Sleep Timer, tạm dừng nhạc khi hết giờ"""
        while self.sleep_time > 0 and self.sleep_timer_running:
            time.sleep(1)
            self.sleep_time -= 1

        if self.sleep_timer_running:
            self.sleep_timer_running = False  # Đánh dấu hẹn giờ đã kết thúc
            if not self.parent.songs.is_paused:
                self.parent.songs.pause_and_resume_song()  # Gọi hàm pause thay vì dừng nhạc

    def stop_sleep_timer(self):
        """Hủy Sleep Timer"""
        if hasattr(self, "sleep_window") and self.sleep_window.winfo_exists():
            self.sleep_window.withdraw()




if __name__ == "__main__":
    app=MainScreen()