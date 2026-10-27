import json
import os
import shutil
import subprocess


def find_usb_drives():
    # Find USB drives and their mounted partitions
    result = subprocess.run(
        ["lsblk", "-J", "-o", "NAME,TRAN,RM,MOUNTPOINT"], capture_output=True, text=True
    )

    # Return no drives if detection fails
    if result.returncode != 0:
        print("Could not detect USB drives.")
        return []

    # Convert the command output into a Python dictionary
    devices = json.loads(result.stdout)
    drives = []

    # Check each storage device
    for device in devices.get("blockdevices", []):
        if device.get("tran") == "usb" or device.get("rm"):
            # Check mounted partitions
            for partition in device.get("children", []):
                mountpoint = partition.get("mountpoint")

                if mountpoint and os.path.isdir(mountpoint):
                    drives.append(mountpoint)

            # Check whether the device itself is mounted
            mountpoint = device.get("mountpoint")

            if mountpoint and os.path.isdir(mountpoint):
                drives.append(mountpoint)

    # Remove duplicate mount paths
    return list(dict.fromkeys(drives))


def pull_usb_images(output_folder):
    # Create a folder for copied images
    os.makedirs(output_folder, exist_ok=True)

    # Find mounted USB drives
    drives = find_usb_drives()

    if not drives:
        print("No mounted USB drives detected.")
        return

    images_found = 0

    # Search each USB drive
    for drive in drives:
        print(f"Searching USB drive: {drive}")

        for root, folders, files in os.walk(drive):
            # Skip system and recycle-bin folders
            folders[:] = [
                folder
                for folder in folders
                if folder not in ("System Volume Information", "$RECYCLE.BIN")
            ]

            # Find supported image files
            for filename in files:
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    source = os.path.join(root, filename)

                    # Choose a destination filename
                    name, extension = os.path.splitext(filename)
                    destination = os.path.join(output_folder, filename)
                    count = 1

                    # Avoid overwriting files with the same name
                    while os.path.exists(destination):
                        destination = os.path.join(
                            output_folder, f"{name}_{count}{extension}"
                        )
                        count += 1

                    try:
                        # Copy the image to the Raspberry Pi
                        shutil.copy2(source, destination)
                        images_found += 1
                        print(f"Copied: {filename}")

                    except OSError as error:
                        print(f"Could not copy {source}: {error}")

    # Display the final results
    print(f"Finished! Copied {images_found} images.")
    print(f"Images saved in: {output_folder}")


if __name__ == "__main__":
    try:
        # Start copying images
        pull_usb_images("/home/ubuntu/Downloads/images/original")

    except Exception as error:
        print(f"An error occurred: {error}")

    import runpy

    runpy.run_module("transmitter_code", run_name="__main__")
