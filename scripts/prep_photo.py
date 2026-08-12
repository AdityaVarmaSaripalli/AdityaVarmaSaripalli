"""
prep_photo.py — Remove background, boost local contrast, composite on white.
Run once per photo: python scripts/prep_photo.py source-photo.png
Output: source-prepped.png
"""

import sys
import os
import numpy as np
import cv2
from PIL import Image
from rembg import remove

INPUT = sys.argv[1] if len(sys.argv) > 1 else "source-photo.png"
OUTPUT = "source-prepped.png"


def prep(input_path: str, output_path: str) -> None:
    with open(input_path, "rb") as f:
        raw = f.read()

    # 1. Remove background
    no_bg = remove(raw)
    img = Image.open(__import__("io").BytesIO(no_bg)).convert("RGBA")

    # 2. Composite on pure white
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    white.paste(img, mask=img.split()[3])
    gray = white.convert("L")

    # 3. Boost local contrast with CLAHE
    arr = np.array(gray, dtype=np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(arr)
    result = Image.fromarray(enhanced)
    result.save(output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    if not os.path.exists(INPUT):
        print(f"Error: {INPUT} not found")
        sys.exit(1)
    prep(INPUT, OUTPUT)
