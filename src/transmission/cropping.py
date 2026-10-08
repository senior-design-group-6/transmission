import os

import cv2
import numpy as np


def find_red_circle(image, min_radius=10, max_radius=2000):
    """
    Looks for a red circle anywhere in the image using contour detection.
    Returns (x, y, r) — center coordinates and radius — or None if no shape found.
    """
    # Slight blur to smooth out noise
    blurred = cv2.GaussianBlur(image, (5, 5), 0)

    # Convert to HSV color space
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Slightly expanded HSV ranges to handle shadows and different shades of red
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Clean up the mask (remove small background specks, fill holes)
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    # Find contours of the red shapes anywhere in the image
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None  # No red shapes found

    # Find the largest red contour in the image
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the minimum enclosing circle around that red shape
    (x, y), radius = cv2.minEnclosingCircle(largest_contour)
    x, y, r = int(x), int(y), int(radius)

    # Filter out shapes that are too small or too big
    if r < min_radius or r > max_radius:
        return None

    return (x, y, r)


def crop_around_circle(image, x, y, r, padding=1.3):
    """
    Crops a square region centered on (x, y), sized to fit the circle
    plus some padding.
    """
    h, w = image.shape[:2]
    pad_r = int(r * padding)

    x1 = max(x - pad_r, 0)
    y1 = max(y - pad_r, 0)
    x2 = min(x + pad_r, w)
    y2 = min(y + pad_r, h)

    return image[y1:y2, x1:x2]


def process_folder(input_dir, matched_dir, padding=1.3):
    """
    Processes every image. If a red circle is found anywhere, crops around it.
    If NOT found, falls back to center-cropping so all images process.
    """
    os.makedirs(matched_dir, exist_ok=True)
    valid_exts = (".jpg", ".jpeg", ".png")

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(valid_exts):
            continue

        path = os.path.join(input_dir, filename)
        image = cv2.imread(path)

        if image is None:
            print(f"Could not read {filename}, skipping.")
            continue

        result = find_red_circle(image)

        if result is not None:
            x, y, r = result
            print(f"[MATCH]    {filename}: red circle found at ({x},{y}), radius {r}")
        else:
            # Fallback if nothing red is detected
            h, w = image.shape[:2]
            x, y = w // 2, h // 2
            r = min(w, h) // 4
            print(
                f"[FALLBACK] {filename}: no red circle found, center-cropping instead"
            )

        # Crop and save
        cropped = crop_around_circle(image, x, y, r, padding=padding)
        out_path = os.path.join(matched_dir, filename)
        cv2.imwrite(out_path, cropped)


if __name__ == "__main__":
    process_folder(
        input_dir=r"C:\Users\danes\Desktop\Sample images team projects",
        matched_dir="output/with_red_circle",
        padding=7.0,  # Adjust padding size here
    )
