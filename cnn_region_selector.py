"""
CNN-Based Intelligent Region Selector for Steganography
Classifies image regions as suitable/unsuitable for embedding
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image
import os
from typing import Tuple, List
import cv2


class CNNRegionSelector:
    """Uses pre-trained CNN to identify suitable regions for steganography"""

    def __init__(self, model_path: str = None):
        """
        Initialize CNN region selector

        Args:
            model_path: Path to pre-trained .keras or .h5 model
                       Tries my_model.keras and cnn_stego_model.h5 if None
        """
        self.model = None
        self.patch_size = 64
        self.stride = 32

        # Try to load model from specified path or defaults
        if model_path:
            self._load_model(model_path)
        else:
            # Try default paths
            for default_path in ["cnn_stego_model.keras", "cnn_stego_model.h5"]:
                if os.path.exists(default_path):
                    try:
                        self._load_model(default_path)
                        print(f"✅ Loaded model from {default_path}")
                        break
                    except Exception as e:
                        print(f"⚠️ Failed to load {default_path}: {e}")

        if self.model is None:
            print("⚠️ WARNING: CNN model not loaded. Using fallback edge detection.")

    def _load_model(self, model_path: str):
        """Load the pre-trained CNN model"""
        try:
            self.model = load_model(model_path, compile=False)
            print(f"✅ CNN Model loaded from {model_path}")
            print(f"   Input shape: {self.model.input_shape}")
            print(f"   Output shape: {self.model.output_shape}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.model = None

    def _normalize_patch(self, patch: np.ndarray) -> np.ndarray:
        """Normalize patch to [0, 1] for CNN inference"""
        if patch.dtype != np.float32:
            patch = patch.astype(np.float32)

        if patch.max() > 1:
            patch = patch / 255.0

        return patch

    def _extract_patches(
        self, image: Image.Image
    ) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """
        Extract overlapping patches from image

        Returns:
            patches: List of image patches
            positions: List of (x, y) positions for each patch
        """
        img_array = np.array(image.convert("RGB"))
        h, w = img_array.shape[:2]

        patches = []
        positions = []

        for y in range(0, h - self.patch_size + 1, self.stride):
            for x in range(0, w - self.patch_size + 1, self.stride):
                patch = img_array[y : y + self.patch_size, x : x + self.patch_size, :]

                # Resize to model input size if needed
                if patch.shape != (self.patch_size, self.patch_size, 3):
                    patch = cv2.resize(patch, (self.patch_size, self.patch_size))

                patches.append(patch)
                positions.append((x, y))

        return patches, positions

    def classify_patches(self, image: Image.Image) -> Tuple[List[int], np.ndarray]:
        """
        Classify image patches as suitable (1) or unsuitable (0) for embedding

        Args:
            image: PIL Image

        Returns:
            suitable_indices: Indices of suitable patches
            confidence_scores: Confidence scores for each patch
        """
        if self.model is None:
            # Fallback: use edge detection
            return self._fallback_edge_detection(image)

        patches, positions = self._extract_patches(image)

        if not patches:
            print("⚠️ No patches extracted from image")
            return list(range(np.array(image).size)), np.ones(np.array(image).size)

        # Normalize patches for CNN
        patches_array = np.array([self._normalize_patch(p) for p in patches])

        # Batch inference
        try:
            predictions = self.model.predict(patches_array, verbose=0)

            # Handle different output formats
            if predictions.ndim == 2:
                # Output shape: (n_patches, 2) - binary classification
                suitable_scores = predictions[:, 1]  # Probability of "suitable" class
            else:
                # Output shape: (n_patches,) - single score
                suitable_scores = predictions.flatten()

            suitable_indices = np.where(suitable_scores > 0.5)[0].tolist()

            return suitable_indices, suitable_scores

        except Exception as e:
            print(f"⚠️ CNN inference error: {e}. Using fallback.")
            return self._fallback_edge_detection(image)

    def get_suitable_pixels(
        self, image: Image.Image, threshold: float = 0.5
    ) -> List[int]:
        """
        Get list of pixel indices marked as suitable for embedding

        Args:
            image: PIL Image
            threshold: Confidence threshold for suitable regions (0-1)

        Returns:
            List of pixel indices in flattened image array
        """
        suitable_patch_indices, scores = self.classify_patches(image)

        if not suitable_patch_indices:
            # Fallback: use all pixels if no suitable patches found
            img_array = np.array(image.convert("RGB"))
            return list(range(img_array.size // 3))

        patches, positions = self._extract_patches(image)
        img_array = np.array(image.convert("RGB"))
        h, w = img_array.shape[:2]

        # Create a binary mask for suitable regions
        mask = np.zeros((h, w), dtype=bool)

        for idx in suitable_patch_indices:
            if idx < len(positions):
                x, y = positions[idx]
                # Mark patch region as suitable
                mask[
                    y : min(y + self.patch_size, h), x : min(x + self.patch_size, w)
                ] = True

        # Convert 2D mask to pixel indices
        suitable_pixels = np.where(mask.flatten())[0].tolist()

        # Ensure we have enough pixels
        if not suitable_pixels:
            suitable_pixels = list(range(img_array.size // 3))

        return suitable_pixels

    def _fallback_edge_detection(
        self, image: Image.Image
    ) -> Tuple[List[int], np.ndarray]:
        """
        Fallback: Use edge detection when CNN is unavailable

        Returns:
            suitable_indices: Indices of suitable patches (all with score 0.7)
            confidence_scores: All patches get score 0.7 (moderate confidence)
        """
        img_array = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Dilate edges to create regions
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        edge_regions = cv2.dilate(edges, kernel, iterations=2)

        # All pixels with edge activity = suitable
        num_pixels = np.prod(edge_regions.shape[:2])
        scores = (edge_regions.flatten() > 0).astype(float) * 0.7 + 0.3

        suitable_indices = np.where(edge_regions.flatten() > 0)[0].tolist()

        if not suitable_indices:
            # If no edges, use all pixels
            suitable_indices = list(range(num_pixels))
            scores = np.ones(num_pixels) * 0.6

        return suitable_indices, scores


# Create global instance
try:
    region_selector = CNNRegionSelector()
except Exception as e:
    print(f"⚠️ Failed to initialize CNN region selector: {e}")
    region_selector = CNNRegionSelector(model_path="dummy")
