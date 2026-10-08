import os
import hashlib
from cryptography.fernet import Fernet


key = b'byUnClxHebyJjGArOKO55S8jHIak8bXtYngtKBxhLk8='

cipher = Fernet(key)

os.makedirs("encryptedPics", exist_ok=True)

for filename in os.listdir("images"): 

    if filename.lower().endswith((".png", ".jpg", ".jpeg")):

        with open(os.path.join("images", filename), "rb") as f:
            data = f.read()

        # MD5 of original image
        md5_hash = hashlib.md5(data).hexdigest()

        # Encrypt image
        encrypted_data = cipher.encrypt(data)

        # Save encrypted image
        output_path = os.path.join(
            "encryptedPics",
            filename + ".enc"
        )

        with open(output_path, "wb") as f:
            f.write(encrypted_data)

        print(f"Encrypted {filename}")
        print(f"MD5: {md5_hash}")

print("Encryption complete.")