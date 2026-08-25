import os
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as transforms

train_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomRotation(5),
    transforms.ColorJitter(brightness=0.1, contrast=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

vit_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

class KaggleDeepfakeDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.transform = transform
        self.image_paths = []
        self.labels = []

        categories = [
            ("fake", 0),
            ("tampered", 0),
            ("authentic", 1),
            ("original", 1),
        ]

        for category, label in categories:
            category_path = os.path.join(data_dir, category)
            if not os.path.exists(category_path):
                continue

            for filename in sorted(os.listdir(category_path)):
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    self.image_paths.append(os.path.join(category_path, filename))
                    self.labels.append(label)

        self.class_to_idx = {
            "fake": 0,
            "tampered": 0,
            "authentic": 1,
            "original": 1,
        }

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label