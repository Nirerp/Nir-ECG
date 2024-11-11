import torch
import torch.nn as nn
import timm


class ECG_Classifier(nn.Module):
    def __init__(self, num_classes=4):
        super(ECG_Classifier, self).__init__()

        # Create the base model
        self.base_model = timm.create_model("efficientnet_b0", pretrained=True)

        # Modify the first convolution layer to accept 1-channel input
        # Get the original first conv layer
        original_conv = self.base_model.conv_stem

        # conv layer with 1 input channel (grayscale) but same output channels as original model
        self.base_model.conv_stem = nn.Conv2d(
            in_channels=1,  # Changed from 3 to 1
            out_channels=original_conv.out_channels,
            kernel_size=original_conv.kernel_size,
            stride=original_conv.stride,
            padding=original_conv.padding,
            bias=False if original_conv.bias is None else True,
        )

        # If using pretrained weights, we need to adapt the weights for the new conv layer
        if original_conv.weight is not None:
            # Average the weights across the 3 channels to create weights for 1 channel
            new_weight = original_conv.weight.data.mean(dim=1, keepdim=True)
            self.base_model.conv_stem.weight.data = new_weight

        self.features = nn.Sequential(*list(self.base_model.children())[:-1])

        enet_out_size = 1280
        self.classifier = nn.Sequential(
            nn.Flatten(), nn.Linear(enet_out_size, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        output = self.classifier(x)
        return output
