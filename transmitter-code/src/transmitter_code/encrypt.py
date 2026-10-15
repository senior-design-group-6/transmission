import hashlib
import os

from cryptography.fernet import Fernet

key = b"byUnClxHebyJjGArOKO55S8jHIak8bXtYngtKBxhLk8="

cipher = Fernet(key)


def encrypt_images(encrypted_pics_path, images_with_red_circle_path):
    os.makedirs(encrypted_pics_path, exist_ok=True)

    for filename in os.listdir(images_with_red_circle_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            with open(
                os.path.join(images_with_red_circle_path, filename),
                "rb",
            ) as f:
                data = f.read()

            # MD5 of original image
            md5_hash = hashlib.md5(data).hexdigest()

            # Encrypt image
            encrypted_data = cipher.encrypt(data)

            # Save encrypted image
            output_path = os.path.join(encrypted_pics_path, filename + ".enc")

            with open(output_path, "wb") as f:
                f.write(encrypted_data)

            print(f"Encrypted {filename}")
            print(f"MD5: {md5_hash}")

    print("Encryption complete.")
