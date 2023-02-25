import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io

class CameraView(tk.Frame):
    def __init__(self, parent, get_data_function):
        tk.Frame.__init__(self, parent)

        self.text1 = ttk.Label(parent, text="Camera view")
        self.text1.pack()

        self.img = None
        self.canvas = tk.Canvas(parent, width=500, height=500)
        self.canvas.pack()

        self.get_data_function = get_data_function
        self.update_image()


    def update_image(self):
        self.after(100, self.update_image)

        img_raw = self.get_data_function()
        if img_raw is None:
            return

        self.img = ImageTk.PhotoImage(Image.open(io.BytesIO(img_raw))) # image must be stored in a persistent variable or else it will get garbage collected (I'm guessing)
        # self.img = Image.open("mars.jpg")
        # self.img = ImageTk.PhotoImage(file="mars.jpg")

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        self.canvas.pack()
