import torchvision.transforms as transforms


def transform(image):
    transform = transforms.Compose(
        [
            transforms.Resize((128, 128)),
            transforms.ToTensor(),
            transforms.Grayscale(num_output_channels=1),
        ]
    )
    return transform(image)
