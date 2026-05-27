"""
Evaluation Metrics for Steganography
PSNR, SSIM, extraction accuracy, payload recovery evaluation
"""

import numpy as np
from PIL import Image
from typing import Tuple, Dict
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


class SteganographyMetrics:
    """Evaluates steganography quality and reliability"""

    @staticmethod
    def calculate_psnr(original: Image.Image, stego: Image.Image) -> float:
        """
        Calculate Peak Signal-to-Noise Ratio
        Higher PSNR = less distortion

        Args:
            original: Original image
            stego: Stego image

        Returns:
            PSNR value in dB
        """
        try:
            original_array = np.array(original.convert("RGB")).astype(np.float32)
            stego_array = np.array(stego.convert("RGB")).astype(np.float32)

            # Handle different array sizes
            min_h = min(original_array.shape[0], stego_array.shape[0])
            min_w = min(original_array.shape[1], stego_array.shape[1])

            original_array = original_array[:min_h, :min_w]
            stego_array = stego_array[:min_h, :min_w]

            psnr = peak_signal_noise_ratio(
                original_array, stego_array, data_range=255.0
            )
            return float(psnr)
        except Exception as e:
            print(f"PSNR calculation error: {e}")
            return 0.0

    @staticmethod
    def calculate_ssim(original: Image.Image, stego: Image.Image) -> float:
        """
        Calculate Structural Similarity Index
        Range: [-1, 1], higher = more similar

        Args:
            original: Original image
            stego: Stego image

        Returns:
            SSIM value
        """
        try:
            original_array = np.array(original.convert("RGB")).astype(np.float32)
            stego_array = np.array(stego.convert("RGB")).astype(np.float32)

            # Handle different array sizes
            min_h = min(original_array.shape[0], stego_array.shape[0])
            min_w = min(original_array.shape[1], stego_array.shape[1])

            original_array = original_array[:min_h, :min_w]
            stego_array = stego_array[:min_h, :min_w]

            ssim = structural_similarity(
                original_array, stego_array, data_range=255.0, channel_axis=2
            )
            return float(ssim)
        except Exception as e:
            print(f"SSIM calculation error: {e}")
            return 0.0

    @staticmethod
    def calculate_mse(original: Image.Image, stego: Image.Image) -> float:
        """
        Calculate Mean Squared Error
        Lower MSE = less distortion

        Args:
            original: Original image
            stego: Stego image

        Returns:
            MSE value
        """
        try:
            original_array = np.array(original.convert("RGB")).astype(np.float32)
            stego_array = np.array(stego.convert("RGB")).astype(np.float32)

            # Handle different array sizes
            min_h = min(original_array.shape[0], stego_array.shape[0])
            min_w = min(original_array.shape[1], stego_array.shape[1])

            original_array = original_array[:min_h, :min_w]
            stego_array = stego_array[:min_h, :min_w]

            mse = np.mean((original_array - stego_array) ** 2)
            return float(mse)
        except Exception as e:
            print(f"MSE calculation error: {e}")
            return 0.0

    @staticmethod
    def extraction_accuracy(original_data: bytes, extracted_data: bytes) -> float:
        """
        Calculate extraction accuracy (bit-perfect recovery)

        Args:
            original_data: Original embedded data
            extracted_data: Extracted data

        Returns:
            Accuracy as percentage (0-100)
        """
        if not original_data:
            return 100.0 if not extracted_data else 0.0

        if len(original_data) != len(extracted_data):
            return 0.0

        # Compare byte-by-byte
        matches = sum(1 for a, b in zip(original_data, extracted_data) if a == b)
        accuracy = (matches / len(original_data)) * 100.0

        return float(accuracy)

    @staticmethod
    def payload_recovery_rate(
        original_data: bytes, extracted_data: bytes
    ) -> Dict[str, any]:
        """
        Evaluate payload recovery

        Args:
            original_data: Original payload
            extracted_data: Extracted payload

        Returns:
            Dictionary with recovery statistics
        """
        is_complete = original_data == extracted_data

        return {
            "is_complete": is_complete,
            "is_bit_perfect": is_complete,
            "original_size": len(original_data),
            "extracted_size": len(extracted_data),
            "extraction_accuracy": SteganographyMetrics.extraction_accuracy(
                original_data, extracted_data
            ),
            "missing_bytes": (
                len(original_data) - len(extracted_data)
                if len(original_data) > len(extracted_data)
                else 0
            ),
            "extra_bytes": (
                len(extracted_data) - len(original_data)
                if len(extracted_data) > len(original_data)
                else 0
            ),
        }

    @staticmethod
    def evaluate_embedding(
        original_image: Image.Image,
        stego_image: Image.Image,
        original_payload: bytes,
        extracted_payload: bytes,
    ) -> Dict[str, any]:
        """
        Comprehensive evaluation of embedding quality

        Args:
            original_image: Original image
            stego_image: Stego image after embedding
            original_payload: Original embedded payload
            extracted_payload: Extracted payload

        Returns:
            Dictionary with all metrics
        """
        recovery = SteganographyMetrics.payload_recovery_rate(
            original_payload, extracted_payload
        )

        return {
            "image_quality": {
                "psnr_db": SteganographyMetrics.calculate_psnr(
                    original_image, stego_image
                ),
                "ssim": SteganographyMetrics.calculate_ssim(
                    original_image, stego_image
                ),
                "mse": SteganographyMetrics.calculate_mse(original_image, stego_image),
            },
            "payload_recovery": recovery,
            "extraction_accuracy_percent": recovery["extraction_accuracy"],
            "is_bit_perfect": recovery["is_bit_perfect"],
            "success": recovery["is_complete"],
        }

    @staticmethod
    def print_evaluation(metrics: Dict[str, any]) -> None:
        """Pretty-print evaluation metrics"""
        print("\n" + "=" * 60)
        print("STEGANOGRAPHY EVALUATION REPORT")
        print("=" * 60)

        print("\n📊 IMAGE QUALITY METRICS:")
        print(f"  PSNR: {metrics['image_quality']['psnr_db']:.2f} dB")
        print(f"  SSIM: {metrics['image_quality']['ssim']:.4f}")
        print(f"  MSE:  {metrics['image_quality']['mse']:.4f}")

        print("\n📦 PAYLOAD RECOVERY METRICS:")
        recovery = metrics["payload_recovery"]
        print(f"  Original Size:    {recovery['original_size']} bytes")
        print(f"  Extracted Size:   {recovery['extracted_size']} bytes")
        print(f"  Extraction Acc:   {recovery['extraction_accuracy']:.2f}%")
        print(
            f"  Bit-Perfect:      {'✅ YES' if recovery['is_bit_perfect'] else '❌ NO'}"
        )

        if recovery["missing_bytes"] > 0:
            print(f"  ⚠️  Missing:       {recovery['missing_bytes']} bytes")
        if recovery["extra_bytes"] > 0:
            print(f"  ⚠️  Extra:         {recovery['extra_bytes']} bytes")

        print("\n" + "=" * 60)
        if metrics["success"]:
            print("✅ OVERALL: SUCCESSFUL EMBEDDING & EXTRACTION")
        else:
            print("❌ OVERALL: FAILED - Data corruption detected")
        print("=" * 60 + "\n")
