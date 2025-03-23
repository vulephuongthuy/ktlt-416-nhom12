from moo_d.ui.Login_UI import LoginScreen
from tkinter import *

if __name__ == "__main__":
    root = Tk()  # Chỉ có một Tk duy nhất
    app = LoginScreen(master=root)
    root.mainloop()