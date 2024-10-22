# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os
import logging

class ImageGenerator:
    def __init__(self, config):
        self.update_config(config)

    def update_config(self, config):
        self.config = config
        self.font_size = config.get('font_size', 48)
        self.font_path = config.get('font_path', "arial.ttf")
        self.image_size = tuple(config.get('image_size', (1920, 1080)))
        self.bg_color = config.get('background_color', 'black')
        self.text_color = config.get('text_color', 'white')
        self.rectangle_color = config.get('rectangle_color', 'white')
        self.px_per_cm = config.get('px_per_cm', 10)
        self.height_shift = config.get('height_shift', 200)
        self.transpose_x = config.get('transpose_x', 0)
        self.transpose_y = config.get('transpose_y', 0)
        
        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except IOError:
            logging.warning(f"Font file {self.font_path} not found. Using default font.")

    def generate_image(self, code):
        # Set background color based on the code
        bg_color = 'red' if code in ["DEBUG1", "DEBUG2"] else self.bg_color
        image = Image.new('RGB', self.image_size, color=bg_color)
        draw = ImageDraw.Draw(image)

        if code == "DEBUG1":
            text = "Read Error"
        elif code == "DEBUG2":
            text = "100x100 mm"
        else:
            image_config = self.config['images'][code]
            text = image_config['text']

        short_width = self.config['images'][code]['short_width'] * self.px_per_cm
        long_width = self.config['images'][code]['long_width'] * self.px_per_cm
        short_height = self.config['short_rectangle_height'] * self.px_per_cm
        long_height = self.config['long_rectangle_height'] * self.px_per_cm

        midpoint_x = self.image_size[0] // 2
        midpoint_y = self.image_size[1] // 2

        # Calculate the positions of the rectangles
        short_x = midpoint_x - short_width // 2 + self.transpose_x
        short_y = midpoint_y - (short_height + long_height) // 2 + self.transpose_y
        long_x = midpoint_x - long_width // 2 + self.transpose_x
        long_y = midpoint_y + (short_height - long_height) // 2 + self.transpose_y

        # Draw short rectangle
        draw.rectangle([short_x, short_y, short_x + short_width, short_y + short_height], fill=self.rectangle_color)

        # Draw long rectangle
        draw.rectangle([long_x, long_y, long_x + long_width, long_y + long_height], fill=self.rectangle_color)

        # Draw text
        text_position = (50, 50)  # Top-left corner with some padding
        draw.text(text_position, text, font=self.font, fill=self.text_color)

        return image

    def save_image(self, code):
        if code in self.config['images']:
            image = self.generate_image(code)
            filename = f"images/{code}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            image.save(filename)
            logging.info(f"Generated and saved image for code: {code}")
            return filename
        else:
            logging.warning(f"No image configuration found for code: {code}")
            return None

    def get_image_path(self, code):
        if code in self.config['images']:
            return f"images/{code}.png"
        else:
            logging.warning(f"No image configuration found for code: {code}")
            return None
