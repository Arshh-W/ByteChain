"""
Face preprocessing pipeline for deepfake detection.
"""

import os
import cv2
from torchvision import transforms


IMAGE_SIZE = 380
MARGIN = 0.20


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CASCADE_PATH = os.path.join(
    BASE_DIR,
    "haarcascade_frontalface_default.xml"
)

if not os.path.exists(CASCADE_PATH):
    raise FileNotFoundError(
        f"Haar cascade not found: {CASCADE_PATH}"
    )

face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

if face_cascade.empty():
    raise RuntimeError(
        "Failed to load Haar cascade"
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


# Experiment 3: training augmentation is DISABLED to test the hypothesis
# that per-image augmentation on 280 images is collapsing the logit band.
# The original (HFlip + Rotation(5) + ColorJitter) list is preserved below
# as a comment so it can be restored after the experiment.
#
# ---- BEGIN: original train_transform (kept as reference) ----
# (Do not uncomment without also setting val_transform / train_transform
#  ordering back if needed. This block is documentation only.)
#
# train_transform_original = transforms.Compose([
#     transforms.ToPILImage(),
#     transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
#     transforms.RandomHorizontalFlip(p=0.5),
#     transforms.RandomRotation(degrees=5),
#     transforms.ColorJitter(
#         brightness=0.2,
#         contrast=0.2
#     ),
#     transforms.ToTensor(),
#     transforms.Normalize(
#         mean=IMAGENET_MEAN,
#         std=IMAGENET_STD
#     ),
# ])
#
# ---- END: original train_transform ----
#
# For this experiment, train_transform == val_transform (no augmentation).
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