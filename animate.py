import sys
import os
import uuid
import random
import numpy as np
from PIL import Image
from main import pixel_sort_rows, pixel_sort_diagonals

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_pipeline(input_path, output_dir, scaled_dir):
    # --- Step 1: Main Processing (Low Res) ---
    img = Image.open(input_path).convert("RGB")
    arr = np.asarray(img)
    
    # Random parameters for Step 1
    thresh1 = random.randint(50, 200)
    min_len1 = random.randint(5, 50)
    thresh2 = random.randint(50, 200)
    min_len2 = random.randint(5, 50)
    
    print(f"    Step 1 (Low Res): T1={thresh1}, L1={min_len1} | T2={thresh2}, L2={min_len2}")
    
    res = pixel_sort_rows(
        arr,
        mask_type="sobel_edges",
        sort_type="by_hue",
        threshold=thresh1,
        min_segment_len=min_len1,
        reverse=False
    )
    
    res = pixel_sort_diagonals(
        res,
        mask_type="luminance",
        sort_type="by_hue",
        threshold=thresh2,
        min_segment_len=min_len2,
        reverse=True
    )
    
    # Save intermediate output
    unique_hash_1 = str(uuid.uuid4())[:8]
    filename = os.path.basename(input_path)
    name_no_ext = os.path.splitext(filename)[0]
    
    output_filename = f"pixel_sorted_{name_no_ext}_{unique_hash_1}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    img_step1 = Image.fromarray(res)
    img_step1.save(output_path)
    
    # --- Step 2: Upscaling & Processing (High Res) ---
    
    # Upscale 3x
    scale_factor = 3
    new_size = (img_step1.width * scale_factor, img_step1.height * scale_factor)
    img_upscaled = img_step1.resize(new_size, resample=Image.Resampling.LANCZOS)
    arr_high = np.asarray(img_upscaled)
    
    # Random parameters for Step 2
    thresh3 = random.randint(50, 200)
    min_len3 = random.randint(15, 100)
    thresh4 = random.randint(50, 200)
    min_len4 = random.randint(15, 100)
    
    print(f"    Step 2 (High Res): T1={thresh3}, L1={min_len3} | T2={thresh4}, L2={min_len4}")

    res_high = pixel_sort_rows(
        arr_high,
        mask_type="sobel_edges",
        sort_type="by_hue",
        threshold=thresh3,
        min_segment_len=min_len3,
        reverse=False
    )

    res_high = pixel_sort_diagonals(
        res_high,
        mask_type="luminance",
        sort_type="by_hue",
        threshold=thresh4,
        min_segment_len=min_len4,
        reverse=True
    )
    
    # Save scaled output
    unique_hash_2 = str(uuid.uuid4())[:8]
    scaled_filename = f"upscaled_{name_no_ext}_{unique_hash_1}_{unique_hash_2}.png"
    scaled_path = os.path.join(scaled_dir, scaled_filename)
    
    img_final = Image.fromarray(res_high)
    img_final.save(scaled_path)
    
    return img_final

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python animate.py <number_of_variations>")
        print("Example: python animate.py 10")
        exit()
        
    try:
        num_variations = int(sys.argv[1])
    except ValueError:
        print("Error: Please provide a valid integer for the number of variations.")
        exit()

    input_dir = "inputs"
    output_dir = "outputs"
    scaled_dir = "scaled"
    animated_dir = "animated"

    ensure_dir(output_dir)
    ensure_dir(scaled_dir)
    ensure_dir(animated_dir)

    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        exit()

    supported_extensions = ('.png', '.jpg', '.jpeg', '.heic', '.bmp', '.tiff')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_extensions)]

    if not files:
        print(f"No images found in '{input_dir}'.")
        exit()

    for filename in files:
        print(f"Creating animation for {filename} with {num_variations} variations...")
        file_path = os.path.join(input_dir, filename)
        
        frames = []
        try:
            for i in range(num_variations):
                print(f"  Variation {i+1}/{num_variations}...")
                frame = process_pipeline(file_path, output_dir, scaled_dir)
                frames.append(frame)
            
            # Save Animation
            name_no_ext = os.path.splitext(filename)[0]
            timestamp = str(uuid.uuid4())[:8]
            anim_filename = f"animation_{name_no_ext}_{timestamp}.gif"
            anim_path = os.path.join(animated_dir, anim_filename)
            
            print(f"Saving animation to {anim_path}...")
            # Duration is in milliseconds per frame. 100ms = 10fps.
            frames[0].save(
                anim_path,
                save_all=True,
                append_images=frames[1:],
                duration=150,
                loop=0
            )
            print("Done!")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
