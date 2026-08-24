"""
Experiment 3: Training script with augmentation DISABLED.

This is a near-clone of src/train.py. The only difference is the output
path: it saves to models/deepfake_b4_augoff.pth so the original baseline
weights in models/deepfake_b4.pth are preserved on disk.

All other variables are identical to the baseline run:
    - SEED = 42, same 280/60/60 split
    - Same EfficientNet-B4 architecture (model.py unchanged)
    - Same optimizer (Adam), same learning rates
    - Same Stage 1 (5 epochs, head-only, lr=1e-4) and
      Stage 2 (10 epochs, last-2-blocks unfrozen, 1e-5/1e-4)
    - Same PATIENCE=5 early stopping rule
    - Same BATCH_SIZE=16
    - Same pos_weight computation

The ONLY change vs the baseline run is:
    preprocess.train_transform == preprocess.val_transform
(no RandomHorizontalFlip, no RandomRotation, no ColorJitter during training).
This was made in src/preprocess.py.

Run:
    python src/train_augoff.py
"""

import os

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from model import DeepfakeDetectorB4
from dataset import (
    DeepfakeDataset,
    collect_samples,
    stratified_split,
    compute_pos_weight,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    SEED,
)


# ---------------------------------------------------------------------------
# Hyperparameters — IDENTICAL to src/train.py
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

# DIFFERENCE vs train.py: separate output path so the baseline weights are
# preserved on disk.
MODEL_PATH = os.path.join(MODEL_DIR, "deepfake_b4_augoff.pth")
STAGE1_BEST_PATH = os.path.join(MODEL_DIR, "stage1_best_augoff.pth")

BATCH_SIZE = 16

# Stage 1: head only
STAGE1_EPOCHS = 5
STAGE1_LR = 1e-4

# Stage 2: unfreeze last N blocks of the backbone
STAGE2_EPOCHS = 10
STAGE2_BACKBONE_LR = 1e-5
STAGE2_HEAD_LR = 1e-4
STAGE2_UNFREEZE_LAST_N_BLOCKS = 2

PATIENCE = 5

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ---------------------------------------------------------------------------
# Helpers — IDENTICAL to src/train.py
# ---------------------------------------------------------------------------

def set_seed(seed=SEED):
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def freeze_backbone(model):
    for param in model.backbone.features.parameters():
        param.requires_grad = False


def unfreeze_last_n_blocks(model, n):
    features = model.backbone.features
    blocks = list(features.children())
    for param in features.parameters():
        param.requires_grad = False
    for block in blocks[-n:]:
        for param in block.parameters():
            param.requires_grad = True


def build_optimizer_stage1(model, lr):
    return torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr,
    )


def build_optimizer_stage2(model, backbone_lr, head_lr):
    backbone_params = []
    head_params = []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if name.startswith("backbone.features"):
            backbone_params.append(param)
        else:
            head_params.append(param)
    return torch.optim.Adam([
        {"params": backbone_params, "lr": backbone_lr},
        {"params": head_params,     "lr": head_lr},
    ])


def run_one_epoch(model, loader, criterion, optimizer, device, train_mode):
    if train_mode:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    all_labels = []
    all_probs = []

    context = torch.enable_grad() if train_mode else torch.no_grad()
    with context:
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device).unsqueeze(1)

            if train_mode:
                optimizer.zero_grad()

            logits = model(images)
            loss = criterion(logits, labels)

            if train_mode:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * labels.size(0)

            probs = torch.sigmoid(logits).detach().cpu().numpy().flatten()
            all_probs.extend(probs.tolist())
            all_labels.extend(labels.detach().cpu().numpy().flatten().tolist())

    avg_loss = total_loss / len(loader.dataset)
    preds = (np.array(all_probs) >= 0.5).astype(int)
    labels_arr = np.array(all_labels).astype(int)

    metrics = {
        "loss": avg_loss,
        "accuracy": accuracy_score(labels_arr, preds),
        "precision": precision_score(labels_arr, preds, zero_division=0),
        "recall": recall_score(labels_arr, preds, zero_division=0),
        "f1": f1_score(labels_arr, preds, zero_division=0),
    }
    try:
        metrics["roc_auc"] = roc_auc_score(labels_arr, all_probs)
    except ValueError:
        metrics["roc_auc"] = float("nan")

    return metrics


def format_metrics(metrics):
    return (
        f"loss={metrics['loss']:.4f} "
        f"acc={metrics['accuracy'] * 100:.2f}% "
        f"prec={metrics['precision']:.3f} "
        f"rec={metrics['recall']:.3f} "
        f"f1={metrics['f1']:.3f} "
        f"auc={metrics['roc_auc']:.3f}"
    )


# ---------------------------------------------------------------------------
# Main training routine
# ---------------------------------------------------------------------------

def train():
    print(f"Using device: {DEVICE}")
    print(f"Output path:  {MODEL_PATH}")
    print("Experiment 3: training augmentation is DISABLED.")
    set_seed(SEED)

    # --- Data ---------------------------------------------------------------
    print("\n[1/5] Collecting samples and splitting dataset...")
    samples = collect_samples(DATA_DIR)
    n_real = sum(1 for _, l in samples if l == 0)
    n_fake = sum(1 for _, l in samples if l == 1)
    print(f"  Total samples: {len(samples)} (real={n_real}, fake={n_fake})")

    if len(samples) < 50:
        raise ValueError(
            f"Only {len(samples)} samples found. You need at least ~50 for "
            "a meaningful training run."
        )

    train_samples, val_samples, test_samples = stratified_split(
        samples, TRAIN_RATIO, VAL_RATIO, TEST_RATIO, seed=SEED,
    )
    print(
        f"  Split sizes: train={len(train_samples)}, "
        f"val={len(val_samples)}, test={len(test_samples)}"
    )

    pos_weight = compute_pos_weight(train_samples)
    print(f"  pos_weight (for BCE loss): {pos_weight.item():.3f}")

    train_dataset = DeepfakeDataset(train_samples, training=True)
    val_dataset = DeepfakeDataset(val_samples, training=False)

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0,
    )

    # --- Model --------------------------------------------------------------
    print("\n[2/5] Building model...")
    model = DeepfakeDetectorB4(pretrained=True).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(DEVICE))

    # --- Stage 1: frozen backbone ------------------------------------------
    print("\n[3/5] Stage 1: training head with frozen backbone")
    freeze_backbone(model)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    print(f"  Trainable params: {n_trainable:,} / {n_total:,}")

    optimizer = build_optimizer_stage1(model, STAGE1_LR)

    best_val_loss = float("inf")
    epochs_since_improvement = 0

    for epoch in range(1, STAGE1_EPOCHS + 1):
        train_metrics = run_one_epoch(
            model, train_loader, criterion, optimizer, DEVICE, train_mode=True,
        )
        val_metrics = run_one_epoch(
            model, val_loader, criterion, optimizer, DEVICE, train_mode=False,
        )

        print(
            f"  Stage 1 epoch {epoch}/{STAGE1_EPOCHS} | "
            f"train {format_metrics(train_metrics)} | "
            f"val {format_metrics(val_metrics)}"
        )

        if val_metrics["loss"] < best_val_loss - 1e-6:
            best_val_loss = val_metrics["loss"]
            epochs_since_improvement = 0
            os.makedirs(MODEL_DIR, exist_ok=True)
            torch.save(model.state_dict(), STAGE1_BEST_PATH)
            print(f"    -> New best val_loss; saved checkpoint to {STAGE1_BEST_PATH}")
        else:
            epochs_since_improvement += 1
            if epochs_since_improvement >= PATIENCE:
                print(
                    f"    -> Early stopping at epoch {epoch} (no improvement "
                    f"for {PATIENCE} epochs)"
                )
                break

    # Restore best Stage 1 weights before Stage 2
    model.load_state_dict(torch.load(STAGE1_BEST_PATH, map_location=DEVICE))
    print(f"  Restored best Stage 1 checkpoint (val_loss={best_val_loss:.4f})")

    # --- Stage 2: unfreeze last N blocks -----------------------------------
    print(
        f"\n[4/5] Stage 2: unfreezing last {STAGE2_UNFREEZE_LAST_N_BLOCKS} "
        f"blocks of backbone"
    )
    unfreeze_last_n_blocks(model, STAGE2_UNFREEZE_LAST_N_BLOCKS)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Trainable params: {n_trainable:,} / {n_total:,}")

    optimizer = build_optimizer_stage2(
        model, STAGE2_BACKBONE_LR, STAGE2_HEAD_LR,
    )

    epochs_since_improvement = 0

    for epoch in range(1, STAGE2_EPOCHS + 1):
        train_metrics = run_one_epoch(
            model, train_loader, criterion, optimizer, DEVICE, train_mode=True,
        )
        val_metrics = run_one_epoch(
            model, val_loader, criterion, optimizer, DEVICE, train_mode=False,
        )

        print(
            f"  Stage 2 epoch {epoch}/{STAGE2_EPOCHS} | "
            f"train {format_metrics(train_metrics)} | "
            f"val {format_metrics(val_metrics)}"
        )

        if val_metrics["loss"] < best_val_loss - 1e-6:
            best_val_loss = val_metrics["loss"]
            epochs_since_improvement = 0
            os.makedirs(MODEL_DIR, exist_ok=True)
            torch.save(model.state_dict(), MODEL_PATH)
            print(
                f"    -> New best val_loss; saved FINAL checkpoint to {MODEL_PATH}"
            )
        else:
            epochs_since_improvement += 1
            if epochs_since_improvement >= PATIENCE:
                print(
                    f"    -> Early stopping at epoch {epoch} (no improvement "
                    f"for {PATIENCE} epochs)"
                )
                break

    # --- Done ---------------------------------------------------------------
    print("\n[5/5] Training complete.")
    print(f"  Best validation loss: {best_val_loss:.4f}")
    print(f"  Final model saved to: {MODEL_PATH}")
    print("\nNext step: run evaluation with the augmented-off weights.")
    print("  The existing src/evaluate.py is NOT modified. To point it at the")
    print("  new weights without editing the file, run:")
    print("    python -c \"import evaluate; evaluate.MODEL_PATH = "
          "'models/deepfake_b4_augoff.pth'; "
          "import runpy; runpy.run_module('evaluate', run_name='__main__')\"")


if __name__ == "__main__":
    train()
