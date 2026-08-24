"""
Single-image inference for the photo-only deepfake detector.

Pipeline (matches validation/test):

    IMAGE
      ↓
    preprocess (Haar Cascade, largest face, 20% margin)
      ↓
    RGB conversion
      ↓
    380×380 resize
      ↓
    ImageNet normalization
      ↓
    EfficientNet-B4
      ↓
    RAW LOGIT
      ↓
    SIGMOID EXACTLY ONCE
      ↓
    fake probability
      ↓
    THRESHOLD (0.55, selected on validation set via Youden's J)
      ↓
    REAL / FAKE

Loads: models/deepfake_b4_augoff.pth
"""

import gc
import os
import cv2
import torch

from model import load_model
from preprocess import detect_face, preprocess_for_dataset


# ---------------------------------------------------------------------------
# Constants — fixed by the final experiment protocol
# ---------------------------------------------------------------------------
# Force CPU on Render to avoid CUDA/GPU memory allocation overhead
DEVICE = torch.device("cpu")

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "deepfake_b4_augoff.pth",
)

THRESHOLD = 0.55

# Global singleton handle for lazy loading
_model = None


def get_model():
    """
    Lazy load the model when an endpoint is actually called.
    Prevents startup OOM on free cloud instances (e.g., Render 512MB limit).
    """
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model not found: {MODEL_PATH}"
            )
        _model = load_model(weights_path=MODEL_PATH, device=DEVICE)
        _model.to(DEVICE)
        _model.eval()
    return _model


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
@torch.no_grad()
def detect_image(image_path):
    """
    Run the deepfake detector on a single image.

    Args:
        image_path (str): absolute or relative path to an image file.

    Returns:
        dict with prediction metrics.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Lazy-load model instance
    model = get_model()

    image_tensor = preprocess_for_dataset(
        image_path,
        training=False,
    ).unsqueeze(0).to(DEVICE)

    raw_logit = model(image_tensor)

    # Sigmoid EXACTLY once
    fake_probability = torch.sigmoid(raw_logit).item()
    real_probability = 1.0 - fake_probability

    if fake_probability >= THRESHOLD:
        prediction = "FAKE"
        confidence = fake_probability
    else:
        prediction = "REAL"
        confidence = real_probability

    # Re-run Haar separately to check face detection
    image_bgr = cv2.imread(image_path)
    face = detect_face(image_bgr) if image_bgr is not None else None
    face_detected = face is not None
    fallback_used = not face_detected

    result = {
        "prediction": prediction,
        "confidence": float(confidence),
        "fake_probability": float(fake_probability),
        "real_probability": float(real_probability),
        "threshold": float(THRESHOLD),
        "face_detected": bool(face_detected),
        "fallback_used": bool(fallback_used),
    }

    # Clean up memory after every request
    del image_tensor, raw_logit
    gc.collect()

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python detector.py <image_path>")
        sys.exit(1)

    result = detect_image(sys.argv[1])
    print(result)