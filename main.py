from pillow_heif import register_heif_opener
from PIL import Image
import os
import uuid
import numpy as np
import random
from datetime import datetime
from scipy import ndimage
from typing import Literal

register_heif_opener()

def rgb_to_hsv_numpy(arr):
    """
    Vectorized RGB to HSV conversion using numpy.
    arr: numpy array of shape (..., 3) with values in [0, 1]
    Returns: numpy array of shape (..., 3) with values in [0, 1]
    """
    r = arr[..., 0]
    g = arr[..., 1]
    b = arr[..., 2]

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    v = maxc

    deltac = maxc - minc

    s = np.zeros_like(v)
    # avoid division by zero
    mask = maxc > 0
    s[mask] = deltac[mask] / maxc[mask]

    h = np.zeros_like(v)
    # avoid division by zero
    mask = deltac > 0

    # r is max
    idx = (r == maxc) & mask
    h[idx] = (g[idx] - b[idx]) / deltac[idx]

    # g is max
    idx = (g == maxc) & mask
    h[idx] = 2.0 + (b[idx] - r[idx]) / deltac[idx]

    # b is max
    idx = (b == maxc) & mask
    h[idx] = 4.0 + (r[idx] - g[idx]) / deltac[idx]

    h = (h / 6.0) % 1.0

    return np.stack([h, s, v], axis=-1)

def rgb_to_luminance(rgb):
    # luminance values go from 0 to 255
    r, g, b = rgb[...,0].astype(float), rgb[...,1].astype(float), rgb[...,2].astype(float)
    return 0.2126*r + 0.7152*g + 0.0722*b

def rgb_to_gray(rgb):
    # standard luminance transform
    return (0.2126*rgb[...,0] +
            0.7152*rgb[...,1] +
            0.0722*rgb[...,2]).astype(np.float32)

def rgb_to_hue(arr):
    # arr: uint8, shape (H, W, 3)
    rgb = arr.astype(np.float32) / 255.0
    hsv = rgb_to_hsv_numpy(rgb)
    hue = hsv[..., 0]
    return hue

sorting_handler = {
    "by_luminance": rgb_to_luminance,
    "by_hue": rgb_to_hue
}

def generate_sorting(sort_type: Literal["by_hue", "by_luminance"], array):
    sorting_function = sorting_handler[sort_type]
    return sorting_function(array)

def sobel_edges(array):
    gray = rgb_to_gray(array)

    gx = ndimage.sobel(gray, axis=1)
    gy = ndimage.sobel(gray, axis=0)

    mag = np.hypot(gx, gy)
    mag = (mag / mag.max() * 255).astype(np.uint8)
    return mag

def generate_mask(mask_type: Literal["luminance", "sobel_edges"], array, threshold):
    if mask_type == "luminance":
        lum_array = rgb_to_luminance(array)
        return lum_array > threshold
    elif mask_type == "sobel_edges":
        edge_array = sobel_edges(array)
        return edge_array < threshold


def pixel_sort_columns(array, mask_type, sort_type,
                       threshold=100, min_segment_len=5, reverse=False,
                       pre_loaded_mask=None):
    """
    array: numpy array shape (H, W, 3), dtype uint8
    """
    height, width, colour = array.shape
    output = array.copy()

    if pre_loaded_mask is not None:
        mask_full = pre_loaded_mask
    else:
        mask_full = generate_mask(mask_type, output, threshold)

    for x in range(width):
        column = output[:,x,:]

        mask = mask_full[:,x]

        i = 0
        while i < height:
            if not mask[i]:
                i += 1
                continue
            j = i
            while j < height and mask[j]:
                j += 1
            if (j - i) >= min_segment_len:
                segment = column[i:j]
                key = generate_sorting(sort_type, segment)
                order = np.argsort(key)
                if reverse:
                    order = order[::-1]
                column[i:j] = segment[order]
            i = j
    return output

def pixel_sort_rows(array, mask_type, sort_type,
                    threshold=100, min_segment_len=5, reverse=False,
                    pre_loaded_mask=None):
    """
    array: numpy array shape (H, W, 3), dtype uint8
    """
    height, width, colour = array.shape
    output = array.copy()

    if pre_loaded_mask is not None:
        mask_full = pre_loaded_mask
    else:
        mask_full = generate_mask(mask_type, output, threshold)

    for y in range(height):
        row = output[y,:,:]

        mask = mask_full[y,:]

        i = 0
        while i < width:
            if not mask[i]:
                i += 1
                continue
            j = i
            while j < width and mask[j]:
                j += 1
            if (j - i) >= min_segment_len:
                segment = row[i:j]
                key = generate_sorting(sort_type, segment)
                order = np.argsort(key)
                if reverse:
                    order = order[::-1]
                row[i:j] = segment[order]
            i = j
    return output

def pixel_sort_diagonals(array, mask_type, sort_type,
                         threshold=100, min_segment_len=5, reverse=False,
                         pre_loaded_mask=None):
    H, W, _ = array.shape
    out = array.copy()

    if pre_loaded_mask is not None:
        mask_full = pre_loaded_mask
    else:
        mask_full = generate_mask(mask_type, out, threshold)

    for d in range(-(H - 1), W):
        coords = []
        for y in range(H):
            x = y + d
            if 0 <= x < W:
                coords.append((y, x))

        if not coords:
            continue

        diag_pixels = np.array([out[y, x] for (y, x) in coords])
        diag_mask   = np.array([mask_full[y, x] for (y, x) in coords])

        i = 0
        L = len(coords)
        while i < L:
            if not diag_mask[i]:
                i += 1
                continue

            j = i
            while j < L and diag_mask[j]:
                j += 1

            if (j - i) >= min_segment_len:
                segment = diag_pixels[i:j]
                key = generate_sorting(sort_type, segment)
                order = np.argsort(key)
                if reverse:
                    order = order[::-1]
                diag_pixels[i:j] = segment[order]

            i = j

        for k, (y, x) in enumerate(coords):
            out[y, x] = diag_pixels[k]

    return out

if __name__ == "__main__":
    input_dir = "inputs"
    output_dir = "outputs"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created '{input_dir}' directory. Please place your images there and run the script again.")
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
            arr = np.asarray(img)

            # Randomize parameters for variation
            thresh1 = random.randint(50, 200)
            min_len1 = random.randint(5, 50)
            
            thresh2 = random.randint(50, 200)
            min_len2 = random.randint(5, 50)

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
            output_filename = f"pixel_sorted_{os.path.splitext(filename)[0]}_{unique_hash}.png"
            output_path = os.path.join(output_dir, output_filename)
            
            out_img = Image.fromarray(res)
            out_img.save(output_path)
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")