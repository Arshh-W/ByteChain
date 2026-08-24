import torch
import torch.nn as nn
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights


class DeepfakeDetectorB4(nn.Module):

    def __init__(self, pretrained=True):

        super(DeepfakeDetectorB4, self).__init__()

        weights = (
            EfficientNet_B4_Weights.DEFAULT
            if pretrained
            else None
        )

        self.backbone = efficientnet_b4(
            weights=weights
        )

        in_features = (
            self.backbone.classifier[1].in_features
        )

        self.backbone.classifier = nn.Sequential(
            nn.Dropout(
                p=0.4,
                inplace=True
            ),

            nn.Linear(
                in_features,
                128
            ),

            nn.ReLU(),

            nn.Dropout(
                p=0.2
            ),

            nn.Linear(
                128,
                1
            )
        )

    def forward(self, x):

        return self.backbone(x)


def load_model(
    weights_path=None,
    device="cpu"
):

    model = DeepfakeDetectorB4(
        pretrained=weights_path is None
    )

    if weights_path:

        state_dict = torch.load(
            weights_path,
            map_location=device
        )

        model.load_state_dict(
            state_dict
        )

        print(
            f"Loaded trained weights from: {weights_path}"
        )

    model.to(device)

    model.eval()

    return model


if __name__ == "__main__":

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    net = DeepfakeDetectorB4(
        pretrained=True
    )

    dummy_input = torch.randn(
        1,
        3,
        380,
        380
    )

    dummy_input = dummy_input.to(device)

    net = net.to(device)

    output = net(
        dummy_input
    )

    print(
        "Model initialized successfully!"
    )

    print(
        f"Output shape: {output.shape}"
    )