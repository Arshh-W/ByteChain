"""
Image analysis utilities used by the ByteChain verification endpoint.

This module wires the FastAPI backend to the existing production
deepfake detector that lives in SIH-ML-Models/src/detector.py.

The detector is loaded once at import time and reused for every
subsequent request (its internal `_model` is already a module-level
singleton). We resolve all paths relative to the ByteChain project
root so the repository is portable.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Path setup — make the production detector importable without moving
# SIH-ML-Models/ inside server/. The detector's own internal paths
# (model weights, Haar cascade) are resolved relative to its own
# location, so simply putting SIH-ML-Models/src on sys.path is enough.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_SRC_DIR = os.path.join(PROJECT_ROOT, "SIH-ML-Models", "src")

if ML_SRC_DIR not in sys.path:
    sys.path.insert(0, ML_SRC_DIR)

# Importing this module loads the trained EfficientNet-B4 weights
# exactly once. Subsequent requests reuse the same model object.
from detector import detect_image  # noqa: E402


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def analyze_image(file_path: str) -> tuple[float, bool]:
    """
    Run the production deepfake detector on a stored image file.

    Returns a tuple ``(confidence_score, is_tampered)`` in the shape the
    existing FastAPI endpoint and database expect:
        - confidence_score : float in [0, 1] (probability of the predicted class)
        - is_tampered      : True if the prediction is FAKE, else False
    """
    result = predict_image(file_path)
    confidence_score = float(result["confidence"])
    is_tampered = bool(result["prediction"] == "FAKE")
    return confidence_score, is_tampered


def predict_image(file_path: str) -> Dict[str, Any]:
    """
    Run the production deepfake detector and return its full structured
    result unchanged:
        {
            "prediction":       "REAL" | "FAKE",
            "confidence":       float in [0, 1],
            "fake_probability": float in [0, 1],
            "real_probability": float in [0, 1],
            "threshold":        float,
            "face_detected":    bool,
            "fallback_used":    bool,
        }
    """
    return detect_image(file_path)
