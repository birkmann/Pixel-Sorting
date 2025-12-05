import os
import sys
import uuid
from PIL import Image, ImageSequence

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def center_crop_to_square(img):
    width, height = img.size
    new_size = min(width, height)
    
    left = (width - new_size) / 2
    top = (height - new_size) / 2
    right = (width + new_size) / 2
    bottom = (height + new_size) / 2

    return img.crop((left, top, right, bottom))

def process_gifs(input_dir, output_dir):
    ensure_dir(output_dir)
    
    supported_extensions = ('.gif',)
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_extensions)]
    
    if not files:
        print(f"No GIFs found in '{input_dir}'.")
        return

    all_frames = []
    
    print(f"Found {len(files)} GIFs. Processing...")
    
    # First pass: Determine the target size (smallest square dimension across all GIFs)
    min_dimension = float('inf')
    
    for filename in files:
        file_path = os.path.join(input_dir, filename)
        try:
            with Image.open(file_path) as img:
                w, h = img.size
                min_dimension = min(min_dimension, w, h)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    print(f"Target crop size: {min_dimension}x{min_dimension}")

    # Second pass: Crop and collect frames
    for filename in files:
        print(f"  Merging {filename}...")
        file_path = os.path.join(input_dir, filename)
        
        try:
            with Image.open(file_path) as img:
                for frame in ImageSequence.Iterator(img):
                    # Convert to RGB to ensure consistency
                    frame_rgb = frame.convert("RGB")
                    
                    # Center crop to square
                    cropped = center_crop_to_square(frame_rgb)
                    
                    # Resize to the common minimum dimension if necessary
                    # (Though center_crop_to_square returns a square of size min(w,h) of THAT image.
                    #  We need to resize it to the GLOBAL min_dimension to match all images.)
                    if cropped.size != (min_dimension, min_dimension):
                        cropped = cropped.resize((min_dimension, min_dimension), Image.Resampling.LANCZOS)
                        
                    all_frames.append(cropped)
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if not all_frames:
        print("No frames collected.")
        return

    unique_hash = str(uuid.uuid4())[:8]
    output_filename = f"final_merged_loop_{unique_hash}.gif"
    output_path = os.path.join(output_dir, output_filename)
    print(f"Saving merged animation with {len(all_frames)} frames to {output_path}...")
    
    # Save as looping GIF
    all_frames[0].save(
        output_path,
        save_all=True,
        append_images=all_frames[1:],
        duration=150, # 150ms per frame
        loop=0
    )
    print("Done!")

if __name__ == "__main__":
    input_dir = "animated"
    output_dir = "final"
    
    process_gifs(input_dir, output_dir)
