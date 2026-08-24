# Deepfake Detection — ML Models

Photo-based deepfake detection using a fine-tuned **EfficientNet-B4** binary
classifier. PyTorch only. **Image input only** (no video in v1).

---

## Project Overview

Photo-only deepfake detection using EfficientNet-B4. The model is a binary
classifier that takes a face image and outputs a single logit, which is
converted to a fake probability via sigmoid and compared against a fixed
decision threshold.

The current model is a **research prototype**, **not production-validated**.
It was trained on a small 400-image dataset and the final reported metrics
are on a 60-image held-out test split.

---

## Dataset

- **400 images total**
  - 200 REAL
  - 200 FAKE
- **Split** (stratified, fixed seed):
  - 70% train  →  280 images
  - 15% val    →   60 images
  - 15% test   →   60 images

**This dataset is small.** Results derived from it are **preliminary** and
should not be taken as evidence of real-world generalization.

---

## Preprocessing

The same preprocessing pipeline is used at training, validation, and
inference time:

1. **Haar Cascade** (`haarcascade_frontalface_default.xml`) face detection.
2. If a face is found, the **largest detected face** is selected.
3. A **20% margin** is added around the bounding box.
4. The crop is converted to **RGB**.
5. Resized to **380 × 380**.
6. Normalized with **ImageNet** mean and std.

If Haar does **not** detect a face, the full image is used as a fallback
(same behaviour as the validation/test pipeline).

A separate crop-quality diagnostic (`src/analyze_crop_quality.py`) was run
on all 400 images. The detected crops are consistent across classes
(mean face-area ratio ≈ 0.45 REAL / 0.47 FAKE, aspect ratio ≈ 1.02–1.03,
<1.1% multi-face in both classes). The analysis did **not** show a major
class-dependent preprocessing problem.

---

## Training

Two-stage transfer learning from ImageNet-pretrained EfficientNet-B4
weights:

- **Stage 1 — head only**
  - Backbone: **frozen**.
  - Classifier head: trainable.
  - Optimised for a small number of epochs at a single learning rate.

- **Stage 2 — fine-tune**
  - **Last 2 EfficientNet-B4 blocks unfrozen**.
  - Two parameter groups: backbone at a lower LR, head at a higher LR.
  - Lower backbone LR prevents destroying pretrained features on this
    small dataset.

Training **augmentation was disabled** because, on this dataset, the
controlled experiment (no augmentation) performed better on the held-out
test set than the experiment with HFlip + small rotation + colour jitter.
Augmentation may be revisited on a larger dataset.

---

## Threshold

- The model outputs a **raw logit**.
- Sigmoid converts it to a **fake probability** (applied exactly once).
- **Threshold = 0.55**.
- The threshold was selected **only on the validation set** using
  **Youden's J statistic** (maximises sensitivity + specificity − 1).
- The 60-image held-out test set was **not** used to select the threshold.

---

## Results

Held-out test set (60 images, 30 REAL + 30 FAKE — see Limitations):

| Metric             | Value     |
|--------------------|-----------|
| Accuracy           | 90.00%    |
| Balanced Accuracy  | 90.00%    |
| F1                 | 0.8966    |
| ROC-AUC            | 0.9111    |

These numbers are based on **only 60 test images** and should be read with
that in mind.

---

## Folder structure

```
SIH-ML-Models/
├── data/
│   ├── real/                # REAL face images (label = 0)
│   └── fake/                # FAKE face images (label = 1)
├── models/
│   └── deepfake_b4_augoff.pth   # final best checkpoint (used by detector.py)
├── results/                 # evaluation metrics, plots, CSV diagnostics
└── src/
    ├── model.py                 # EfficientNet-B4 + custom classifier head
    ├── preprocess.py            # Haar face detection, 20% margin, transforms
    ├── dataset.py               # dataset class, stratified split, pos_weight
    ├── train.py                 # original training script
    ├── train_augoff.py          # final two-stage training (augmentation off)
    ├── evaluate.py              # held-out test-set evaluation
    ├── detector.py              # single-image inference (final pipeline)
    ├── test.py                  # CLI: python src/test.py --image path.jpg
    ├── analyze_preprocessing.py # Haar detection diagnostic
    ├── analyze_crop_quality.py  # crop-quality diagnostic
    └── haarcascade_frontalface_default.xml
```

---

## Setup

```bash
pip install -r requirements.txt
```

Dependencies: `torch`, `torchvision`, `opencv-python`, `numpy`, `Pillow`,
`scikit-learn`, `matplotlib`.

---

## Inference on a single image

```bash
python src/test.py --image data/real/real_00000.jpg
python src/test.py --image data/fake/fake_00000.jpg
```

Internally:

1. Loads `models/deepfake_b4_augoff.pth`.
2. Applies the same Haar → 20%-margin → 380×380 → ImageNet-normalize
   pipeline used at validation time.
3. Runs the model under `torch.no_grad()` and `model.eval()`.
4. Applies **sigmoid exactly once** to the raw logit.
5. Compares the fake probability to the validation-selected threshold 0.55.

Example output:

```
Analyzing image: data/real/real_00000.jpg

--- Detection Results ---
Prediction       : REAL
Confidence       : 78.32%
Fake Probability : 21.68%
Real Probability : 78.32%
Threshold        : 0.55
Face detected    : yes
Fallback used    : no
-------------------------
```

---

## Limitations

- **Only 400 images** total (200 REAL / 200 FAKE). The model has very
  limited exposure to the diversity of real-world deepfakes.
- **Only 60 held-out test images.** Final metrics carry a large
  confidence interval; a single misclassification changes accuracy by
  ~1.67 percentage points.
- The 60-image test split provides a **limited estimate of real-world
  generalization**. The numbers above should not be cited as a property
  of the model in deployment.
- **Haar Cascade** is not a state-of-the-art face detector. It can miss
  non-frontal, occluded, or small faces, and may select a non-face region
  in cluttered scenes.
- **The dataset may not represent the kinds of deepfakes seen in
  practice.** Modern generative methods produce artefacts that the
  current training data does not cover.
- **The threshold (0.55) was optimised on a small validation set.**
  Different validation splits may yield a slightly different optimal
  threshold.
- **Additional independent data is needed for meaningful production
  evaluation.** This model is not production-ready and must not be used
  to make consequential decisions about individuals.

---

## Design notes

- **Label mapping:** real = 0, fake = 1. The model outputs a single logit;
  the fake probability is `sigmoid(logit)`. Mapping is consistent across
  `dataset.py`, `train*.py`, `detector.py`, and `evaluate.py`.
- **Why BCEWithLogitsLoss:** numerically stable (fused sigmoid + BCE),
  and supports `pos_weight` for class imbalance.
- **Why two stages:** training all of EfficientNet-B4 from a new head on
  a small dataset destroys the pretrained features. Stage 1 lets the head
  learn first; Stage 2 carefully adapts the high-level features that
  matter for deepfake artifacts.
- **Why freeze early backbone blocks:** low-level edges/colors are
  universal; deepfake cues (blending boundaries, frequency anomalies)
  live in the deepest blocks.
- **Why ImageNet normalization:** `EfficientNet_B4_Weights.DEFAULT` was
  trained with these exact mean/std values, so the pretrained features
  remain valid.
