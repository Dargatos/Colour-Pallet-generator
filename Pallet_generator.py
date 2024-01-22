import colorsys
from datetime import datetime
from PIL import Image
from itertools import chain

# Here are a lot of functions unused im planing on using them later tho not so far to use them atm

class ColorGenerator:
    def __init__(self, smoothness=100, num_arrays=3, test_mode=True, percentage=None, file_name='Autumn Leaves', rainbow=False, alternating=False):
        self.smoothness = smoothness
        self.num_arrays = num_arrays
        self.test_mode = test_mode
        self.percentage = percentage if percentage is not None else int(smoothness / num_arrays)
        self.file_name = file_name
        self.rainbow = rainbow
        self.alternating = alternating
        self.all_colors = []
        self.reference_colors = []

    def generate_gradient_colors(self, reference_colors, num_colors):
        num_refs = len(reference_colors)
        colors = []

        for i in range(num_colors):
            hue = i / float(num_colors-1)
            ref_index = int(hue * (num_refs - 1))
            remainder = hue * (num_refs - 1) - ref_index
            color1_rgb = tuple(int(reference_colors[ref_index][j:j + 2], 16) for j in (1, 3, 5))

            if ref_index < num_refs - 1:
                color2_rgb = tuple(int(reference_colors[ref_index + 1][j:j + 2], 16) for j in (1, 3, 5))
                rgb = [int(color1_rgb[j] + remainder * (color2_rgb[j] - color1_rgb[j])) for j in range(3)]
            else:
                rgb = color1_rgb

            hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
            colors.append(hex_color)
        return colors

    def generate_rainbow_colors(self, num_colors):
        colors = []
        for i in range(num_colors):
            hue = i / float(num_colors)
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            rgb_int = [int(val * 255) for val in rgb]
            hex_color = "#{:02X}{:02X}{:02X}".format(*rgb_int)
            colors.append(hex_color)
        return colors

    
    def create_color_image(self,color_array):
        num_colors = len(color_array)

        # Calculate the image size based on a square image
        image_size = int(num_colors ** 0.5)
        if image_size**2 < num_colors:
            image_size += 1

        # Create a new image with RGBA mode to support transparency
        image = Image.new("RGBA", (image_size, image_size))

        # Assign each color to a pixel in the image
        for i, hex_color in enumerate(color_array):
            # Convert hex color codes to RGB tuple
            rgb_color = tuple(int(hex_color[j:j + 2], 16) for j in (1, 3, 5))
            # Set alpha value to 255 (fully opaque)
            rgba_color = rgb_color + (255,)

            # Calculate pixel coordinates
            x, y = i % image_size, i // image_size
            # Assign color to the pixel
            image.putpixel((x, y), rgba_color)

        # Resize the image to be more visually appealing
        final_image_size = 256
        image = image.resize((final_image_size, final_image_size), Image.NEAREST)

        return image

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def save_colors_to_file(self, colors, name, directory):
        filename = f'{directory}/{name}.txt'
        with open(filename, 'w') as file:
            for color in colors:
                file.write(color + '\n')

    def save_image(self, image, prefix='color_image'):
        file_info = f'{len(self.alternated_colors)}'
        current_time = datetime.now().strftime('%Y.%m.%d_%H_%M_%S')
        filename = f'C:\\Users\\Mio\\AppData\\Roaming\\SoundSpacePlus\\images_form_colors\\{self.file_name}__{file_info}-{prefix}_{current_time}.png'
        image.save(filename)
        print(f"Image saved to {filename}")

    def generate_colors(self):
        # Define reference colors for the first array
        reference_colors1 = ["#FF6347", "#FFA07A", "#FFD700", "#8B4513", "#8B0000"]

        # Generate gradient between the reference colors for the first array
        gradient_colors1 = self.generate_gradient_colors(reference_colors1, self.percentage)

        # Define reference colors for the second array
        reference_colors2 = ["#00E5D4", "#0E00E5", "#BC00E5"]

        # Generate gradient between the reference colors for the second array
        if self.alternating:
            gradient_colors2 = self.generate_gradient_colors(reference_colors2, self.percentage)

        # Combine and alternate the generated colors into a new array
        if self.rainbow is False:
            if self.alternating:
                alternated_colors = list(chain.from_iterable(zip(gradient_colors1, gradient_colors2)))
            else:
                alternated_colors = gradient_colors1
        else:
            if len(gradient_colors1) != len(gradient_colors2):
                raise ValueError("Arrays have not the same length")
            alternated_colors = self.generate_rainbow_colors(self.smoothness)

        self.all_colors = alternated_colors
        return alternated_colors

    def display_image(self):
        color_image = self.create_color_image(self.all_colors, image_width=100)
        self.save_colors_to_file(self.all_colors, prefix='Co')
        self.save_image(color_image, prefix='color_image')
        color_image.show()


# Example of usage:
#color_gen = ColorGenerator(smoothness=100, num_arrays=3, test_mode=True, percentage=None,
#                           file_name='Autumn Leaves', rainbow=False, alternating=False)
#generated_colors = color_gen.generate_colors()
#color_gen.display_image()
