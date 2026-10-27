import os

import cv2
import numpy as np


def find_red_circle(
    image: np.ndarray,
    min_radius: int = 10,
    max_radius: int = 2000,
    min_circularity: float = 0.65,
) -> tuple[int, int, int] | None:
    """Detect a red circle using HSV color filtering and contour analysis."""

    # Convert BGR to HSV.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Wider red ranges to accommodate color variation.
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([12, 255, 255])

    lower_red2 = np.array([168, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    red_mask = cv2.bitwise_or(mask1, mask2)

    # Remove noise and close small gaps.
    kernel = np.ones((3, 3), np.uint8)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        red_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if area <= 0 or perimeter <= 0:
            continue

        # Reject contours that are not sufficiently circular.
        circularity = 4 * np.pi * area / (perimeter**2)

        if circularity < min_circularity:
            continue

        (x, y), radius = cv2.minEnclosingCircle(contour)

        if not min_radius <= radius <= max_radius:
            continue

        # Reject contours whose filled area is too small
        # relative to their enclosing circle.
        circle_area = np.pi * radius**2

        if circle_area <= 0:
            continue

        fill_ratio = area / circle_area

        if fill_ratio < 0.55:
            continue

        candidates.append((circularity * area, int(x), int(y), int(radius)))

    if not candidates:
        return None

    _, x, y, r = max(candidates, key=lambda candidate: candidate[0])

    return x, y, r


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


def crop_images(images_folder, cropped_images_folder, padding=1.3):
    """
    Processes every image. If a red circle is found anywhere, crops around it.
    If NOT found, falls back to center-cropping so all images process.
    """
    os.makedirs(cropped_images_folder, exist_ok=True)
    valid_exts = (".jpg", ".jpeg", ".png")

    for filename in os.listdir(images_folder):
        if not filename.lower().endswith(valid_exts):
            continue

        path = os.path.join(images_folder, filename)
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
            print(f"[FALLBACK] {filename}: no red circle found")
            continue

        # Crop and save
        cropped = crop_around_circle(image, x, y, r, padding=padding)
        out_path = os.path.join(cropped_images_folder, filename)
        cv2.imwrite(out_path, cropped)
