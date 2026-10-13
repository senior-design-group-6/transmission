import os
import hashlib
import requests
from cryptography.fernet import Fernet

# Must be the exact same key as encrypt.py
key = b'byUnClxHebyJjGArOKO55S8jHIak8bXtYngtKBxhLk8='

cipher = Fernet(key)

# Create decrypted folder
os.makedirs("decryptedPics", exist_ok=True)

# Store decrypted images so we can upload them together
files_to_upload = []

# Decrypt the files
for filename in os.listdir("encryptedPics"):

    if filename.endswith(".enc"):

        # Read encrypted image
        with open(os.path.join("encryptedPics", filename), "rb") as f:
            encrypted_data = f.read()

        # Decrypt image
        decrypted_data = cipher.decrypt(encrypted_data)

        # Get original filename
        original_filename = filename[:-4]

        # Create MD5 checksum
        md5_hash = hashlib.md5(decrypted_data).hexdigest()

        # Save decrypted image
        output_path = os.path.join(
            "decryptedPics",
            original_filename
        )

        with open(output_path, "wb") as f:
            f.write(decrypted_data)

        print("Decrypted:", original_filename)
        print("MD5:", md5_hash)

        # Add image to upload list
        files_to_upload.append(
            (
                "image",
                (
                    original_filename,
                    open(output_path, "rb"),
                    "image/jpeg"
                )
            )
        )


# Upload all decrypted images
if len(files_to_upload) > 0:

    response = requests.post(
        "https://seniorprojectsite.onrender.com/upload-images/", 
        files=files_to_upload 
    ) 

    if response.status_code == 200 or response.status_code == 303: 
        print("Images uploaded successfully!") 
    else: 
        print("Upload failed.") 
        print("Status code:", response.status_code) 
        print("Server response:", response.text) 

    # Close the image files 
    for item in files_to_upload: 
        item[1][2].close() 

print("Decryption and upload complete.")