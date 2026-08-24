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

import os

import cv2
import torch

from model import load_model
from preprocess import detect_face, preprocess_for_dataset


# ---------------------------------------------------------------------------
# Constants — fixed by the final experiment protocol
# ---------------------------------------------------------------------------
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

# Final best model — produced by the augoff (Experiment 3) training run.
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "deepfake_b4_augoff.pth",
)

# Threshold selected ONLY on the validation set via Youden's J statistic.
# The 60-image held-out test set was NOT used to tune this value.
THRESHOLD = 0.55


# ---------------------------------------------------------------------------
# Model loading — fail loudly if the checkpoint is missing
# ---------------------------------------------------------------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Trained model not found: {MODEL_PATH}"
    )

_model = load_model(weights_path=MODEL_PATH, device=DEVICE)
_model.eval()  # defense in depth — load_model also calls .eval()


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
        dict with keys:
            prediction        : "REAL" or "FAKE"
            confidence        : float in [0, 1] — probability of the predicted class
            fake_probability  : float in [0, 1]
            real_probability  : float in [0, 1]
            threshold         : float — the decision threshold used
            face_detected     : bool — whether Haar found a face
            fallback_used     : bool — whether the full image was used as fallback

    Raises:
        FileNotFoundError : if image_path does not exist
        ValueError        : if the image cannot be read by OpenCV
        RuntimeError      : if model inference fails for any other reason
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image_tensor = preprocess_for_dataset(
        image_path,
        training=False,   # never use training augmentation at inference time
    ).unsqueeze(0).to(DEVICE)

    raw_logit = _model(image_tensor)

    # Sigmoid EXACTLY once — never inside the model, never inside the loss.
    fake_probability = torch.sigmoid(raw_logit).item()
    real_probability = 1.0 - fake_probability

    if fake_probability >= THRESHOLD:
        prediction = "FAKE"
        confidence = fake_probability
    else:
        prediction = "REAL"
        confidence = real_probability

    # Re-run Haar separately (cheap) so we can report whether a face was
    # detected. preprocess_for_dataset returns the same answer internally.
    image_bgr = cv2.imread(image_path)
    face = detect_face(image_bgr) if image_bgr is not None else None
    face_detected = face is not None
    fallback_used = not face_detected

    return {
        "prediction": prediction,
        "confidence": float(confidence),
        "fake_probability": float(fake_probability),
        "real_probability": float(real_probability),
        "threshold": float(THRESHOLD),
        "face_detected": bool(face_detected),
        "fallback_used": bool(fallback_used),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python detector.py <image_path>")
        sys.exit(1)

    result = detect_image(sys.argv[1])
    print(result)
