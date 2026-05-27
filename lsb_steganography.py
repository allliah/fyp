"""
Deterministic LSB (Least Significant Bit) Steganography
100% bit-perfect embedding and extraction with payload framing
"""

import numpy as np
from PIL import Image
from typing import Tuple, List
import struct


class LSBSteganography:
    """
    Deterministic LSB embedding/extraction for 100% bit-perfect recovery
    Uses payload framing with magic header and length field
    """

    MAGIC_HEADER = b"STEGO_v2"  # 8-byte magic header
    PAYLOAD_HEADER_SIZE = 12  # 8 bytes magic + 4 bytes length
    BITS_PER_CHANNEL = 1  # Use only LSB of each channel

    @staticmethod
    def _build_payload(data: bytes) -> bytes:
        """
        Build embedding payload with header

        Format:
        [8 bytes: MAGIC_HEADER][4 bytes: data_length][data]

        Args:
            data: Raw data to embed

        Returns:
            Framed payload with header
        """
        frame = LSBSteganography.MAGIC_HEADER
        frame += struct.pack(">I", len(data))  # Big-endian 4-byte length
        frame += data
        return frame

    @staticmethod
    def _parse_payload(data: bytes) -> bytes:
        """
        Parse embedding payload with header validation

        Args:
            data: Extracted payload

        Returns:
            Extracted data without header, or empty bytes if invalid
        """
        if len(data) < LSBSteganography.PAYLOAD_HEADER_SIZE:
            return b""

        # Check magic header
        if data[:8] != LSBSteganography.MAGIC_HEADER:
            return b""

        # Extract length
        try:
            length = struct.unpack(">I", data[8:12])[0]
        except:
            return b""

        # Validate length
        if length > len(data) - LSBSteganography.PAYLOAD_HEADER_SIZE:
            return b""

        # Extract data
        return data[12 : 12 + length]

    @staticmethod
    def _bytes_to_bits(data: bytes) -> str:
        """Convert bytes to binary string (MSB first)"""
        return "".join(format(b, "08b") for b in data)

    @staticmethod
    def _bits_to_bytes(bits: str) -> bytes:
        """Convert binary string to bytes"""
        # Pad to multiple of 8
        if len(bits) % 8 != 0:
            bits = bits.ljust(len(bits) + (8 - len(bits) % 8), "0")

        return bytes(int(bits[i : i + 8], 2) for i in range(0, len(bits), 8))

    @staticmethod
    def embed(
        image: Image.Image, data: bytes, suitable_pixels: List[int] = None
    ) -> Image.Image:
        """
        Embed data into image using LSB steganography

        Args:
            image: PIL Image (RGB or RGBA)
            data: Data to embed
            suitable_pixels: Pixel indices to use (if None, uses all)

        Returns:
            Stego image with embedded data

        Raises:
            ValueError: If data too large for image
        """
        img_array = np.array(image.convert("RGB"))
        h, w, c = img_array.shape
        total_pixels = h * w

        # Build payload
        payload = LSBSteganography._build_payload(data)
        payload_bits = LSBSteganography._bytes_to_bits(payload)

        # Check capacity
        if suitable_pixels is None:
            suitable_pixels = list(range(total_pixels))

        capacity_bits = len(suitable_pixels) * LSBSteganography.BITS_PER_CHANNEL
        if len(payload_bits) > capacity_bits:
            raise ValueError(
                f"Data too large: {len(payload_bits)} bits needed, "
                f"but only {capacity_bits} bits available"
            )

        # Flatten image
        flat = img_array.flatten()

        # Embed bits into suitable pixels
        for i, bit in enumerate(payload_bits):
            pixel_idx = suitable_pixels[i]
            # Set LSB
            flat[pixel_idx] = (flat[pixel_idx] & 0xFE) | int(bit)

        # Reshape and convert back
        stego_array = flat.reshape(img_array.shape).astype(np.uint8)
        return Image.fromarray(stego_array, mode="RGB")

    @staticmethod
    def extract(
        image: Image.Image,
        suitable_pixels: List[int] = None,
        max_bytes: int = 1_000_000,
    ) -> bytes:
        """
        Extract data from stego image

        Args:
            image: Stego image
            suitable_pixels: Pixel indices used (if None, tries all)
            max_bytes: Maximum bytes to extract (safety limit)

        Returns:
            Extracted data (empty bytes if no valid payload found)
        """
        img_array = np.array(image.convert("RGB"))
        h, w = img_array.shape[:2]
        total_pixels = h * w

        if suitable_pixels is None:
            suitable_pixels = list(range(total_pixels))

        flat = img_array.flatten()

        # Try to extract header first
        header_bits_needed = LSBSteganography.PAYLOAD_HEADER_SIZE * 8

        if len(suitable_pixels) < header_bits_needed:
            return b""

        # Extract header bits
        bits = ""
        for i in range(header_bits_needed):
            pixel_idx = suitable_pixels[i]
            bits += str(flat[pixel_idx] & 1)

        # Parse header
        try:
            header = LSBSteganography._bits_to_bytes(bits)
            if header[:8] != LSBSteganography.MAGIC_HEADER:
                return b""

            length = struct.unpack(">I", header[8:12])[0]
        except:
            return b""

        # Validate length
        if length > max_bytes:
            return b""

        payload_bits_needed = LSBSteganography.PAYLOAD_HEADER_SIZE * 8 + length * 8

        if len(suitable_pixels) < payload_bits_needed:
            return b""

        # Extract full payload
        bits = ""
        for i in range(payload_bits_needed):
            pixel_idx = suitable_pixels[i]
            bits += str(flat[pixel_idx] & 1)

        # Parse payload
        payload = LSBSteganography._bits_to_bytes(bits)
        return LSBSteganography._parse_payload(payload)
