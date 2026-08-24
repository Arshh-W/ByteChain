"""
Dataset and splitting utilities for deepfake detection.

Label convention:
    0 = REAL
    1 = FAKE
"""

import os

import numpy as np
import torch
from torch.utils.data import Dataset

from preprocess import preprocess_for_dataset


TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

SEED = 42


def collect_samples(data_dir):
    """
    Collect image paths and labels from:

        data/real/
        data/fake/

    Returns:
        [(image_path, label), ...]
    """

    samples = []

    for label, subdir in [(0, "real"), (1, "fake")]:

        class_dir = os.path.join(
            data_dir,
            subdir
        )

        if not os.path.isdir(class_dir):
            raise FileNotFoundError(
                f"Expected directory not found: {class_dir}"
            )

        for filename in sorted(os.listdir(class_dir)):

            path = os.path.join(
                class_dir,
                filename
            )

            if os.path.isfile(path):
                samples.append(
                    (path, label)
                )

    return samples


class DeepfakeDataset(Dataset):

    def __init__(
        self,
        samples,
        training=False
    ):
        self.samples = samples
        self.training = training

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label = self.samples[index]

        tensor = preprocess_for_dataset(
            image_path,
            training=self.training
        )

        label_tensor = torch.tensor(
            label,
            dtype=torch.float32
        )

        return tensor, label_tensor


def stratified_split(
    samples,
    train_ratio=TRAIN_RATIO,
    val_ratio=VAL_RATIO,
    test_ratio=TEST_RATIO,
    seed=SEED
):
    """
    Split the dataset into train/validation/test
    while keeping the Real/Fake ratio balanced.
    """

    assert abs(
        train_ratio +
        val_ratio +
        test_ratio -
        1.0
    ) < 1e-6, "Ratios must sum to 1.0"

    rng = np.random.default_rng(seed)

    by_class = {
        0: [],
        1: []
    }

    for path, label in samples:
        by_class[label].append(path)

    train_samples = []
    val_samples = []
    test_samples = []

    for label, paths in by_class.items():

        paths = list(paths)

        rng.shuffle(paths)

        n = len(paths)

        n_train = int(
            round(n * train_ratio)
        )

        n_val = int(
            round(n * val_ratio)
        )

        train_samples.extend(
            (path, label)
            for path in paths[:n_train]
        )

        val_samples.extend(
            (path, label)
            for path in paths[
                n_train:
                n_train + n_val
            ]
        )

        test_samples.extend(
            (path, label)
            for path in paths[
                n_train + n_val:
            ]
        )

    rng.shuffle(train_samples)
    rng.shuffle(val_samples)
    rng.shuffle(test_samples)

    return (
        train_samples,
        val_samples,
        test_samples
    )


def compute_pos_weight(samples):
    """
    Compute the positive-class weight for BCEWithLogitsLoss.

    Real = 0
    Fake = 1

    pos_weight = number_of_real / number_of_fake
    """

    n_real = sum(
        1
        for _, label in samples
        if label == 0
    )

    n_fake = sum(
        1
        for _, label in samples
        if label == 1
    )

    if n_fake == 0:
        return torch.tensor(
            [1.0],
            dtype=torch.float32
        )

    weight = n_real / n_fake

    return torch.tensor(
        [weight],
        dtype=torch.float32
    )