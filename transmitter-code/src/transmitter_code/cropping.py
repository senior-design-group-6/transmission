import os

import cv2
import numpy as np


def find_red_circle(
    image: np.ndarray,
    min_radius: int = 15,
    max_radius: int = 35,
    min_circularity: float = 0.80,
) -> tuple[int, int, int] | None:
    """
    Detect a thin red circular outline using contour hierarchy.

    Specifically targets red ring annotations rather than
    filled red objects, glowing lights, or red image details.

    Returns:
        (center_x, center_y, radius), or None.
    """

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Isolate strongly saturated, bright-red pixels.
    mask1 = cv2.inRange(
        hsv,
        np.array([0, 150, 130]),
        np.array([10, 255, 255]),
    )

    mask2 = cv2.inRange(
        hsv,
        np.array([170, 150, 130]),
        np.array([179, 255, 255]),
    )

    red_mask = cv2.bitwise_or(mask1, mask2)

    # RETR_TREE preserves the relationship between
    # the outer and inner boundaries of a red ring.
    contours, hierarchy = cv2.findContours(
        red_mask,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    if hierarchy is None:
        return None

    hierarchy = hierarchy[0]
    candidates = []

    for i, outer in enumerate(contours):
        # Only consider top-level contours.
        if hierarchy[i][3] != -1:
            continue

        outer_area = cv2.contourArea(outer)
        outer_perimeter = cv2.arcLength(outer, True)

        if outer_area <= 0 or outer_perimeter <= 0:
            continue

        # Check the outer contour's circularity.
        outer_circularity = 4 * np.pi * outer_area / outer_perimeter**2

        if outer_circularity < min_circularity:
            continue

        (x, y), outer_radius = cv2.minEnclosingCircle(outer)

        if not min_radius <= outer_radius <= max_radius:
            continue

        # A ring must contain an inner contour (hole).
        child_index = hierarchy[i][2]

        while child_index != -1:
            inner = contours[child_index]

            inner_area = cv2.contourArea(inner)
            inner_perimeter = cv2.arcLength(inner, True)

            if inner_area > 0 and inner_perimeter > 0:
                inner_circularity = 4 * np.pi * inner_area / inner_perimeter**2

                (ix, iy), inner_radius = cv2.minEnclosingCircle(inner)

                # Inner and outer circles must be concentric.
                center_distance = np.hypot(x - ix, y - iy)

                # The ring should have a thin, consistent border.
                radius_ratio = inner_radius / outer_radius

                if (
                    inner_circularity >= min_circularity
                    and center_distance <= 2.0
                    and 0.70 <= radius_ratio <= 0.95
                ):
                    score = (
                        outer_circularity
                        * inner_circularity
                        * (1 - center_distance / outer_radius)
                    )

                    candidates.append(
                        (
                            score,
                            round(x),
                            round(y),
                            round(outer_radius),
                        )
                    )

            # Check additional child contours, if any.
            child_index = hierarchy[child_index][0]

    if not candidates:
        return None

    _, x, y, radius = max(candidates, key=lambda c: c[0])

    return x, y, radius


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
            print(f"[REJECTED] {filename}: no red marker found")
            continue

        # Crop and save
        cropped = crop_around_circle(image, x, y, r, padding=padding)
        out_path = os.path.join(cropped_images_folder, filename)
        cv2.imwrite(out_path, cropped)
