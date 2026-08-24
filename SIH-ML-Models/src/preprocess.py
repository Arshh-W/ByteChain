"""
Face preprocessing pipeline for deepfake detection.
"""

import os
import cv2
from torchvision import transforms


IMAGE_SIZE = 380
MARGIN = 0.20

# Use OpenCV's built-in Haar cascade path directly from the package
CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    raise RuntimeError(
        f"Failed to load Haar cascade from built-in path: {CASCADE_PATH}"
    )


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


val_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=IMAGENET_MEAN,
        std=IMAGENET_STD
    ),
])

train_transform = val_transform
test_transform = val_transform


def detect_face(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    if len(faces) == 0:
        return None

    x, y, w, h = max(
        faces,
        key=lambda face: face[2] * face[3]
    )

    return x, y, w, h


def crop_face(image, face):

    x, y, w, h = face

    margin_x = int(w * MARGIN)
    margin_y = int(h * MARGIN)

    x1 = max(
        0,
        x - margin_x
    )

    y1 = max(
        0,
        y - margin_y
    )

    x2 = min(
        image.shape[1],
        x + w + margin_x
    )

    y2 = min(
        image.shape[0],
        y + h + margin_y
    )

    return image[
        y1:y2,
        x1:x2
    ]


def preprocess_for_dataset(
    image_path,
    training=False
):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    face = detect_face(image)

    if face is not None:
        image = crop_face(
            image,
            face
        )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    if training:
        tensor = train_transform(image)
    else:
        tensor = val_transform(image)

    return tensor