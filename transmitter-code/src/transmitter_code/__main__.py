from pathlib import Path

from .cropping import crop_images
from .encrypt import encrypt_images
from .transmitter import transmit_images
from .usb_scraper import pull_usb_images


def main() -> None:
    print("Hello from transmitter-code!")

    images_root = Path.home() / "Downloads" / "images"
    original_dir = images_root / "original"
    cropped_dir = images_root / "with_red_circle"
    encrypted_dir = images_root / "encrypted_pics"

    # 1. Pull Images from USB
    pull_usb_images(output_folder=original_dir)

    # 2. Crop Images
    crop_images(
        images_folder=original_dir,
        cropped_images_folder=cropped_dir,
        padding=1.5,  # Adjust padding size here
    )

    # 3. Encrypt Images
    encrypt_images(
        images_with_red_circle_path=cropped_dir,
        encrypted_pics_path=encrypted_dir,
    )

    # 4. Transmit images
    transmit_images(
        image_folder_to_compress=encrypted_dir,
        image_archive_name=images_root / "deathstarplans.7z",
    )

    print("Transmission Complete!")


if __name__ == "__main__":
    main()
