# --- Receiver ---
import struct  # Allows raw bytes to be converted back and foth to regular numbers.
import zlib  # crc 32 checksum calculations

import serial  # Uses Pyserial Library

chunk_size = 230  # Chunk Size, any smaller slows down the transmission, any larger causes errors when I experimented with it.
MAGIC = b"\xaa\x55"  # Marks the start of a packet with a two byte marker
output_path = r"C:\Users\jacob\Downloads\receivedimage.7z"

xbee2 = serial.Serial(
    port="COM6", baudrate=115200, timeout=20
)  # timeout = how long to wait for an ACK. Make sure port is correct for device and baudrate matches other Xbee


def send_reply(kind, seq):
    xbee2.write(kind + struct.pack(">I", seq))  # Sends reply based on what is received.
    xbee2.flush()


def wait_for_magic():  # Waits for 2 bytes that start a packet.
    """Scan the stream one byte at a time until the start marker is found."""
    window = b""
    while True:
        b = xbee2.read(1)
        if not b:
            return False  # Timed out
        window = (window + b)[-2:]
        if window == MAGIC:
            return True


print("Waiting for data...")
expected_seq = 0  # Sets expected packet order.
packet_num = 0

with open(output_path, "wb") as f:  # Writes incoming file
    while True:
        if not wait_for_magic():
            print("No data received in the last 20s, ending transmission")
            break

        header = xbee2.read(
            6
        )  # reads the 4 byte sequence number and the two byte payload length
        if (
            len(header) != 6
        ):  # If this is 6 bytes total it is confiremd they are all received.
            continue
        seq, length = struct.unpack(">IH", header)
        if (
            length > chunk_size
        ):  # Corrupted header if the length is larger than our chunk size
            send_reply(b"N", expected_seq)
            continue

        payload = xbee2.read(length)
        crc_bytes = xbee2.read(
            4
        )  # Reads the four byte CRC at the end to see if packet made it OK
        if len(payload) != length or len(crc_bytes) != 4:
            send_reply(b"N", expected_seq)  # Packet cut short
            continue

        if (
            zlib.crc32(header + payload) != struct.unpack(">I", crc_bytes)[0]
        ):  # Finds CRC of received packet and compares it to the one received. Packet is probably OK if they match
            print(f"Packet {seq} corrupted, requesting resend")
            send_reply(b"N", seq)
            continue

        if (
            seq == expected_seq
        ):  # Makes sure the packet received is the next one in the sequence.
            if length == 0:  # End marker
                send_reply(b"A", seq)
                print("Received end of transmission marker, transfer complete.")
                break
            f.write(payload)
            expected_seq += 1
            packet_num += 1
            print(f"Received packet {packet_num} ({length} bytes)")
            send_reply(b"A", seq)
        elif seq < expected_seq:
            send_reply(
                b"A", seq
            )  # Duplicate: our ACK was lost, so re-ACK but don't write again
        # seq > expected_seq shouldn't happen with stop-and-wait, so ignore it

print(f"Done. Received {packet_num} packets, saved to {output_path}")
# MD5 check
#
import hashlib

end_seq = expected_seq  # sequence number of the end marker
received_md5 = None

while True:
    if not wait_for_magic():
        print(
            "No MD5 checksum received"
        )  # Repeats transmission process for MD5 checksum
        break
    header = xbee2.read(6)
    if len(header) != 6:
        continue
    seq, length = struct.unpack(">IH", header)
    if length > chunk_size:
        send_reply(b"N", end_seq + 1)
        continue
    payload = xbee2.read(length)
    crc_bytes = xbee2.read(4)
    if len(payload) != length or len(crc_bytes) != 4:
        send_reply(b"N", end_seq + 1)
        continue
    if zlib.crc32(header + payload) != struct.unpack(">I", crc_bytes)[0]:
        send_reply(b"N", seq)
        continue
    if seq == end_seq:  # Duplicate end marker (our ACK was lost), re-ACK it
        send_reply(b"A", seq)
        continue
    if seq == end_seq + 1 and length == 16:  # The MD5 packet
        send_reply(b"A", seq)
        received_md5 = payload
        break

if received_md5 is not None:
    md5 = hashlib.md5()
    with open(output_path, "rb") as f:  # Takes MD5 of 7zip file
        for block in iter(lambda: f.read(65536), b""):
            md5.update(block)
    if (
        md5.digest() == received_md5
    ):  # Checks if received MD5 matches one of currently received file.
        print(f"MD5 checksum MATCHES ({md5.hexdigest()})")
    else:
        print(
            "MD5 checksum MISMATCH! Expected",
            received_md5.hex(),
            "but got",
            md5.hexdigest(),
        )


xbee2.close()

# 7 Zip Unpacking

import os

import py7zr

archive_name = r"C:\Users\jacob\Downloads\receivedimage.7z"
extract_to = r"C:\Users\jacob\Downloads\plans"

# Check that the archive exists
print("Archive exists:", os.path.exists(archive_name))

# Create the destination folder if it doesn't exist
os.makedirs(extract_to, exist_ok=True)

# Extract the 7z archive
with py7zr.SevenZipFile(archive_name, mode="r") as archive:
    archive.extractall(path=extract_to)

print(f"Archive extracted to: {extract_to}")
print("Files extracted:", os.listdir(extract_to))
