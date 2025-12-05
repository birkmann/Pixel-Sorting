from PIL import Image
import os
import uuid
import numpy as np
import random
from main import pixel_sort_rows, pixel_sort_diagonals, pixel_sort_columns

if __name__ == "__main__":
    input_dir = "outputs"
    output_dir = "scaled"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        exit()

    supported_extensions = ('.png', '.jpg', '.jpeg', '.heic', '.bmp', '.tiff')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_extensions)]

    if not files:
        print(f"No images found in '{input_dir}'.")
        exit()

    for filename in files:
        print(f"Processing {filename}...")
        file_path = os.path.join(input_dir, filename)
        
        try:
            img = Image.open(file_path).convert("RGB")
            
            # Upscale 3x
            scale_factor = 3
            new_size = (img.width * scale_factor, img.height * scale_factor)
            print(f"  Upscaling from {img.size} to {new_size}...")
            img = img.resize(new_size, resample=Image.Resampling.LANCZOS)
            
            arr = np.asarray(img)

            # Randomize parameters for variation
            # Using slightly larger minimum segment lengths since the image is larger
            thresh1 = random.randint(50, 200)
            min_len1 = random.randint(15, 100)
            
            thresh2 = random.randint(50, 200)
            min_len2 = random.randint(15, 100)

            print(f"  Iteration 1: threshold={thresh1}, min_len={min_len1}")
            res = pixel_sort_rows(
                arr,
                mask_type="sobel_edges",
                sort_type="by_hue",
                threshold=thresh1,
                min_segment_len=min_len1,
                reverse=False
            )

            print(f"  Iteration 2: threshold={thresh2}, min_len={min_len2}")
            res = pixel_sort_diagonals(
                res,
                mask_type="luminance",
                sort_type="by_hue",
                threshold=thresh2,
                min_segment_len=min_len2,
                reverse=True
            )

            unique_hash = str(uuid.uuid4())[:8]
            output_filename = f"upscaled_{os.path.splitext(filename)[0]}_{unique_hash}.png"
            output_path = os.path.join(output_dir, output_filename)
            
            out_img = Image.fromarray(res)
            out_img.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
