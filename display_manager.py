# display_manager.py
import tkinter as tk
from PIL import ImageTk, Image
import logging

class DisplayManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.configure(background='black')  # Set background to black
        self.canvas = tk.Canvas(self, bg='black', highlightthickness=0)  # Set canvas background to black
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.current_image = None
        self.current_photo = None
        self.bind('<Escape>', self.exit_fullscreen)
        self.bind('<Configure>', self.on_resize)

    def show_image(self, image_path):
        try:
            if self.current_image:
                self.canvas.delete(self.current_image)
            
            image = Image.open(image_path)
            self.current_photo = ImageTk.PhotoImage(image)
            
            self.center_image()
            
            logging.info(f"Displayed image: {image_path} with size: {image.size}")
        except FileNotFoundError:
            logging.error(f"Image file not found: {image_path}")
        except Exception as e:
            logging.error(f"Error displaying image: {str(e)}")

    def center_image(self):
        if self.current_photo:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            image_width = self.current_photo.width()
            image_height = self.current_photo.height()
            
            x = (canvas_width - image_width) // 2
            y = (canvas_height - image_height) // 2
            
            # Clear the entire canvas
            self.canvas.delete("all")
            
            # Create a black rectangle covering the entire canvas
            self.canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill='black', outline='black')
            
            # Draw the image
            self.current_image = self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_photo)
            
            logging.info(f"Image centered at ({x}, {y})")

    def on_resize(self, event):
        if self.current_photo:
            self.center_image()

    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)
        logging.info("Exited fullscreen mode")

    def run(self):
        self.mainloop()
