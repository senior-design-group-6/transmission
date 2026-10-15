from .cropping import crop_images
from .encrypt import encrypt_images
from .transmitter import transmit_images


def main() -> None:
    print("Hello from transmitter-code!")

    # 1. Crop Images
    crop_images(
        images_folder=r"/home/ubuntu/Downloads/images",
        cropped_images_folder=r"/home/ubuntu/Downloads/images/with_red_circle",
        padding=7.0,  # Adjust padding size here
    )

    # 2. Encrypt Images
    encrypt_images(
        encrypted_pics_path=r"/home/ubuntu/Downloads/images/encrypted_pics",
        images_with_red_circle_path=r"/home/ubuntu/Downloads/images/with_red_circle",
    )

    # 3. Transmit images
    transmit_images(
        image_folder_to_compress=r"/home/ubuntu/Downloads/images/encrypted_pics",
        image_archive_name=r"/home/ubuntu/Downloads/deathstarplans.7z",
    )


if __name__ == "__main__":
    main()
