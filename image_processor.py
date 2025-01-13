import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import os
from datetime import datetime

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.current_image = None
        self.photo = None

        # Create main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill='both')

        # Create buttons
        self.load_button = tk.Button(self.main_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        self.invert_button = tk.Button(self.main_frame, text="Invert Image", command=self.invert_image, state='disabled')
        self.invert_button.pack(pady=5)

        self.bw_button = tk.Button(self.main_frame, text="Convert to B&W", command=self.convert_to_bw, state='disabled')
        self.bw_button.pack(pady=5)

        self.rainbow_button = tk.Button(self.main_frame, text="Create Rainbow Collage", command=self.create_rainbow_collage, state='disabled')
        self.rainbow_button.pack(pady=5)

        # Create canvas for image display
        self.canvas = tk.Canvas(self.main_frame, bg='gray', width=500, height=500)
        self.canvas.pack(pady=10)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        if file_path:
            self.current_image = Image.open(file_path)
            self.display_image(self.current_image)
            self.invert_button.config(state='normal')
            self.bw_button.config(state='normal')
            self.rainbow_button.config(state='normal')

    def display_image(self, image):
        # Resize image to fit canvas while maintaining aspect ratio
        display_size = (500, 500)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            250, 250,  # Center of canvas
            image=self.photo,
            anchor='center'
        )

    def invert_image(self):
        if self.current_image:
            inverted_image = ImageOps.invert(self.current_image.convert('RGB'))
            self.current_image = inverted_image
            self.display_image(self.current_image)

    def convert_to_bw(self):
        if self.current_image:
            bw_image = self.current_image.convert('L')
            self.current_image = bw_image
            self.display_image(self.current_image)

    def apply_color_tint(self, image, color):
        # Convert image to RGB if it isn't already
        rgb_image = image.convert('RGB')
        
        # Create color overlay
        overlay = Image.new('RGB', rgb_image.size, color)
        
        # Blend images
        return Image.blend(rgb_image, overlay, 0.3)

    def generate_rainbow_gradient(self, num_colors=49):
        # Define the main rainbow colors as RGB
        rainbow_stops = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (238, 130, 238) # Violet
        ]
        
        # Generate intermediate colors
        colors = []
        segments = len(rainbow_stops) - 1
        colors_per_segment = num_colors // segments
        
        for i in range(segments):
            start_color = rainbow_stops[i]
            end_color = rainbow_stops[i + 1]
            
            for j in range(colors_per_segment):
                ratio = j / colors_per_segment
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                colors.append((r, g, b))
        
        # Add the final color if needed
        if len(colors) < num_colors:
            colors.append(rainbow_stops[-1])
        
        return colors[:num_colors]

    def create_rainbow_collage(self):
        if not self.current_image:
            return

        # Generate 49 colors (25 for inner grid + 24 for border)
        colors = self.generate_rainbow_gradient(49)

        # Calculate sizes
        single_width = self.current_image.width
        single_height = self.current_image.height
        half_width = single_width // 2
        half_height = single_height // 2
        
        # Total size including border
        total_width = single_width * 5 + half_width * 2
        total_height = single_height * 5 + half_height * 2
        
        # Create the base collage
        collage = Image.new('RGB', (total_width, total_height))

        # Place the inner 5x5 grid
        for idx in range(25):
            color = colors[idx]
            tinted = self.apply_color_tint(self.current_image, color)
            x = (idx % 5) * single_width + half_width
            y = (idx // 5) * single_height + half_height
            collage.paste(tinted, (x, y))

        # Create and place border images
        border_colors = colors[25:]
        border_idx = 0

        # Top border
        for i in range(6):
            if border_idx >= len(border_colors): break
            half_img = self.apply_color_tint(self.current_image, border_colors[border_idx])
            half_img = half_img.resize((half_width, half_height))
            x = i * single_width
            collage.paste(half_img, (x, 0))
            border_idx += 1

        # Right border
        for i in range(6):
            if border_idx >= len(border_colors): break
            half_img = self.apply_color_tint(self.current_image, border_colors[border_idx])
            half_img = half_img.resize((half_width, half_height))
            x = total_width - half_width
            y = i * single_height
            collage.paste(half_img, (x, y))
            border_idx += 1

        # Bottom border
        for i in range(6):
            if border_idx >= len(border_colors): break
            half_img = self.apply_color_tint(self.current_image, border_colors[border_idx])
            half_img = half_img.resize((half_width, half_height))
            x = total_width - (i + 1) * single_width
            y = total_height - half_height
            collage.paste(half_img, (x, y))
            border_idx += 1

        # Left border
        for i in range(6):
            if border_idx >= len(border_colors): break
            half_img = self.apply_color_tint(self.current_image, border_colors[border_idx])
            half_img = half_img.resize((half_width, half_height))
            x = 0
            y = total_height - (i + 1) * single_height
            collage.paste(half_img, (x, y))
            border_idx += 1

        # Save and display
        output_dir = os.path.join(os.path.dirname(__file__), 'rainbow_collages')
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(output_dir, f'rainbow_collage_border_{timestamp}.png')
        collage.save(save_path)
        
        messagebox.showinfo("Success", f"Collage saved to:\n{save_path}")
        self.current_image = collage
        self.display_image(self.current_image)

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
