"""
Single-image CLI for the photo-only deepfake detector.

Usage:
    python src/test.py --image path/to/image.jpg
"""

import argparse
import os

from detector import detect_image


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Photo-only deepfake detector (EfficientNet-B4, "
            "Haar crop, threshold=0.55)"
        )
    )

    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the image file",
    )

    args = parser.parse_args()
    image_path = args.image

    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        return 1

    print(f"Analyzing image: {image_path}")

    try:
        result = detect_image(image_path)

        print("\n--- Detection Results ---")
        print(f"Prediction       : {result['prediction']}")
        print(f"Confidence       : {result['confidence'] * 100:.2f}%")
        print(f"Fake Probability : {result['fake_probability'] * 100:.2f}%")
        print(f"Real Probability : {result['real_probability'] * 100:.2f}%")
        print(f"Threshold        : {result['threshold']:.2f}")
        face = "yes" if result["face_detected"] else "no"
        fb = "yes" if result["fallback_used"] else "no"
        print(f"Face detected    : {face}")
        print(f"Fallback used    : {fb}")
        print("-------------------------\n")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except ValueError as e:
        print(f"Preprocessing Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
