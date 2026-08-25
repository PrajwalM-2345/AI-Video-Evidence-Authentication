import os
import random
import matplotlib.pyplot as plt
from PIL import Image

def plot_samples(data_dir, num_samples=4):
    categories = ['authentic', 'fake']
    fig, axes = plt.subplots(2, num_samples, figsize=(12, 6))
    
    for row, category in enumerate(categories):
        category_path = os.path.join(data_dir, category)
        if not os.path.exists(category_path):
            print(f"❌ Path not found: {category_path}")
            continue
            
        images = [f for f in os.listdir(category_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Pick random samples to view
        sampled_images = random.sample(images, min(num_samples, len(images)))
        
        for col, img_name in enumerate(sampled_images):
            img_path = os.path.join(category_path, img_name)
            img = Image.open(img_path)
            
            ax = axes[row, col]
            ax.imshow(img)
            ax.set_title(f"{category.upper()}\n{img_name}", fontsize=10)
            ax.axis('off')
            
    plt.tight_layout()
    print("🎨 Displaying image grid window...")
    plt.show()

if __name__ == "__main__":
    plot_samples(data_dir="kaggle_data/faceforensics_frames")