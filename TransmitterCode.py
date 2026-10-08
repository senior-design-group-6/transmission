# Compresses file to 7 zip

import py7zr  # For 7zip
import os
import hashlib # For MD5

file_to_compress = r"C:\Users\jacob\Downloads\Limage"
archive_name = r"C:\Users\jacob\Downloads\deathstarplans.7z"

# Check that the folder actually exists
print("Folder exists:", os.path.exists(file_to_compress))
print("Files in folder:", os.listdir(file_to_compress))

# Create the 7z archive
with py7zr.SevenZipFile(archive_name, mode="w") as archive:
    archive.writeall(file_to_compress, arcname="images")

print(f"\nArchive created: {archive_name}")
print(f"Archive size: {os.path.getsize(archive_name):,} bytes")

# --- Transmitter ---
import serial
import struct
import zlib

chunk_size = 230
MAX_RETRIES = 15          # Give up on a packet after ten tries
MAGIC = b"\xAA\x55"       # Marks the start of a packet with a two byte marker

xbee1 = serial.Serial(port="COM3", baudrate=115200, timeout=2)  # timeout = how long to wait for an ACK. Make sure port is correct for device and baudrate matches other Xbee

def build_packet(seq, payload): # Makes a function called build packet, where the packets sequence number and data or used in the function
    body = struct.pack(">IH", seq, len(payload)) + payload # Gives each packet a header
    crc = struct.pack(">I", zlib.crc32(body)) # Finds CRC checksum of each packet body
    return MAGIC + body + crc # Complete packet, has the two byte marker, sequence marker, the main body (contains actual data), and the CRC checksum

def send_reliably(seq, payload): # Makes a function that Resends a packet untill it received an ACK back, showing it was received successfully
    packet = build_packet(seq, payload) #Packet is made
    for attempt in range(1, MAX_RETRIES + 1): # Tries to send for "MaxRetry" times
        xbee1.reset_input_buffer()          # Cleans serial inputs buffer
        xbee1.write(packet) #Sends packet
        xbee1.flush() # Waits untill all bytes have been transmitted
        reply = xbee1.read(5)               # 1 byte type ('A' or 'N') + 4 byte sequence number
        if len(reply) == 5 and reply[:1] == b"A" and struct.unpack(">I", reply[1:])[0] == seq: # If ACK is received, success is reported. If not tries to resend
            return True
        print(f"Packet {seq}: no valid ACK (attempt {attempt}/{MAX_RETRIES}), resending...")
    return False

with open(r"C:\users\jacob\Downloads\deathstarplans.7z", "rb") as pics:
    pieces = [] # Addes packets to list
    while True:
        piece = pics.read(chunk_size)
        if not piece:
            break
        pieces.append(piece) # Appends each chunk to list

print(f"Number of pieces: {len(pieces)}")

#Finds MD5

md5 = hashlib.md5()
with open(r"C:\users\jacob\Downloads\deathstarplans.7z", "rb") as f:
    for block in iter(lambda: f.read(65536), b""):
        md5.update(block)
file_md5 = md5.digest()  # 16 bytes
print(f"MD5 of archive: {md5.hexdigest()}")

## 
for seq, chunk in enumerate(pieces):
    if not send_reliably(seq, chunk):
        print(f"Failed to deliver packet {seq + 1} after {MAX_RETRIES} attempts. Aborting.") # Failes if ACK is never received afte so many tries.
        xbee1.close()
        raise SystemExit(1)
    print(f"Sent packet {seq + 1}/{len(pieces)}")

# End-of-transmission = a empty packet
if send_reliably(len(pieces), b""):
    print("Images sent")
else:
    print("All data sent, but the final end marker was not received")

# Send the MD5 checksum as one last packet
if send_reliably(len(pieces) + 1, file_md5):
    print("MD5 checksum sent")
else:
    print("Failed to deliver the MD5 checksum")

xbee1.close()
