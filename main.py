# main.py
import json
import logging
import os
import shutil
from image_generator import ImageGenerator
from display_manager import DisplayManager
from file_watcher import FileWatcher

def setup_logging():
    logging.basicConfig(level=logging.WARNING,  # Change to WARNING to reduce verbosity
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',
                        filemode='a')

def clear_images_directory():
    if os.path.exists('images'):
        shutil.rmtree('images')
    os.makedirs('images')

def pre_generate_images(image_generator):
    for code in image_generator.config['images']:
        image_generator.save_image(code)

def main():
    setup_logging()
    logging.info("Application started")

    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logging.error("Config file not found. Exiting.")
        return
    except json.JSONDecodeError:
        logging.error("Invalid JSON in config file. Exiting.")
        return

    clear_images_directory()  # Clear the images directory
    image_generator = ImageGenerator(config)
    pre_generate_images(image_generator)  # Regenerate images at launch
    
    display_manager = DisplayManager()
    file_watcher = FileWatcher(config, image_generator, display_manager)

    # Display initial image
    initial_code = list(config['images'].keys())[0]  # Get the first image code
    initial_image_path = image_generator.get_image_path(initial_code)
    display_manager.show_image(initial_image_path)

    try:
        file_watcher.start()
        display_manager.after(100, check_for_updates, display_manager, file_watcher)
        display_manager.run()
    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        file_watcher.stop()
        logging.info("Application stopped")

def check_for_updates(display_manager, file_watcher):
    file_watcher.observer.event_queue.join()
    display_manager.after(100, check_for_updates, display_manager, file_watcher)

if __name__ == "__main__":
    main()

# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os

class ImageGenerator:
    def __init__(self, config):
        self.config = config
        self.font = ImageFont.truetype("arial.ttf", 36)

    def generate_image(self, text):
        image = Image.new('RGB', (1920, 1080), color='black')
        draw = ImageDraw.Draw(image)
        draw.text((960, 540), text, font=self.font, fill='white', anchor='mm')
        return image

    def save_image(self, code):
        if code in self.config['images']:
            text = self.config['images'][code]
            image = self.generate_image(text)
            filename = f"images/{code}.png"
            image.save(filename)
            return filename
        return None

    def get_image_path(self, code):
        if code in self.config['images']:
            return f"images/{code}.png"
        return None

# display_manager.py
import tkinter as tk
from PIL import ImageTk, Image

class DisplayManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.current_image = None

    def show_image(self, image_path):
        if self.current_image:
            self.canvas.delete(self.current_image)
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.current_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def run(self):
        self.mainloop()

# file_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class FileWatcher:
    def __init__(self, config, image_generator, display_manager):
        self.config = config
        self.image_generator = image_generator
        self.display_manager = display_manager
        self.observer = Observer()

    def start(self):
        event_handler = FileChangeHandler(self.config, self.image_generator, self.display_manager)
        self.observer.schedule(event_handler, path='.', recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, config, image_generator, display_manager):
        self.config = config
        self.image_generator = image_generator
        self.display_manager = display_manager

    def on_modified(self, event):
        if event.src_path.endswith('Camera_Data.txt'):
            with open(event.src_path, 'r') as file:
                data = file.read().strip()
            image_path = self.image_generator.save_image(data)
            if image_path:
                self.display_manager.show_image(image_path)
