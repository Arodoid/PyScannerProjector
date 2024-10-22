# file_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import logging
import json

class FileWatcher:
    def __init__(self, config, image_generator, display_manager):
        self.config = config
        self.image_generator = image_generator
        self.display_manager = display_manager
        self.observer = Observer()
        self.handler = FileChangeHandler(self.config, self.image_generator, self.display_manager)

    def start(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.observer.schedule(self.handler, path=script_dir, recursive=False)
        self.observer.start()
        logging.info("File watcher started")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logging.info("File watcher stopped")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, config, image_generator, display_manager):
        self.config = config
        self.image_generator = image_generator
        self.display_manager = display_manager
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path.endswith('Camera_Data.txt'):
            current_time = time.time()
            if current_time - self.last_modified > 0.1:  # Debounce threshold
                self.last_modified = current_time
                self.process_camera_data(event.src_path)
        elif event.src_path.endswith('config.json'):
            self.process_config(event.src_path)

    def process_camera_data(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read().strip()
            
            # Log only if the data is recognized or unrecognized
            if data in self.config['images']:
                logging.info(f"Recognized data: {self.config['images'][data]['text']}")
            else:
                logging.warning(f"Unrecognized data: {data}")

            image_path = self.image_generator.get_image_path(data)
            if image_path:
                logging.info(f"Displaying image from path: {image_path}")
                self.display_manager.show_image(image_path)
            else:
                logging.warning(f"No image found for data: {data}")
        except Exception as e:
            logging.error(f"Error processing camera data file: {str(e)}")

    def process_config(self, file_path):
        try:
            with open(file_path, 'r') as config_file:
                new_config = json.load(config_file)
            self.config.update(new_config)
            self.image_generator.update_config(new_config)
            logging.info("Config updated successfully")
        except Exception as e:
            logging.error(f"Error processing config file: {str(e)}")
