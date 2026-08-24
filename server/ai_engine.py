import sys
import os

# Add src to system path so imports work smoothly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

try:
    from detector import detect_image
except ImportError:
    from src.detector import detect_image

def analyze_image(image_path: str):
    """
    Passes image path to our EfficientNet deepfake detection engine.
    Returns: (confidence_score: float, is_tampered_bool: bool)
    """
    results = detect_image(image_path)
    
    confidence_score = float(results["confidence"])
    is_tampered = bool(results["prediction"] == "fake")
    
    return confidence_score, is_tampered