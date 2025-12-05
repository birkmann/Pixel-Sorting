# Pixel Sorting

A Python-based tool for artistic pixel sorting effects, capable of generating high-resolution images, animations, and seamless loops.

Original inspiration: [Reddit Post](https://www.reddit.com/r/generative/comments/1pdv7b7/night_traffic_python_pixel_sorting/)

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install pillow pillow-heif numpy scipy matplotlib
    ```

2.  **Prepare Images:**
    *   Place your source images in the `inputs/` folder.
    *   Supported formats: `.jpg`, `.png`, `.heic`, `.bmp`, `.tiff`.

## Usage

### 1. Full Pipeline (Recommended)
To generate animations and merge them into a final looping GIF in one go:

```bash
# Usage: ./run_pipeline.sh <number_of_variations>
chmod +x run_pipeline.sh
./run_pipeline.sh 10
```
This will:
1.  Generate 10 variations for each image in `inputs/`.
2.  Save intermediate steps to `outputs/` and `scaled/`.
3.  Save individual GIFs to `animated/`.
4.  Merge all GIFs into a single looping animation in `final/`.

### 2. Individual Scripts

#### Single Pass (Low Res)
Process images once with random parameters.
```bash
python3 main.py
```
*   **Input:** `inputs/`
*   **Output:** `outputs/`

#### Upscale & Sort
Take images from `outputs/`, upscale them 3x, and apply a second pass of sorting.
```bash
python3 upscale.py
```
*   **Input:** `outputs/`
*   **Output:** `scaled/`

#### Generate Animations
Generate multiple variations of the full pipeline (Input -> Low Res -> Upscale -> High Res) and save as GIFs.
```bash
# Usage: python3 animate.py <number_of_variations>
python3 animate.py 10
```
*   **Input:** `inputs/`
*   **Output:** `animated/` (GIFs), plus intermediates in `outputs/` and `scaled/`.

#### Finalize (Merge)
Take all GIFs from `animated/`, crop them to squares, and merge them into one seamless loop.
```bash
python3 finalize.py
```
*   **Input:** `animated/`
*   **Output:** `final/`

## Folder Structure
*   `inputs/`: Source images.
*   `outputs/`: First pass sorted images (low res).
*   `scaled/`: Upscaled and second pass sorted images (high res).
*   `animated/`: Individual animations per image.
*   `final/`: Final merged looping GIF.