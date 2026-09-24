import os
import shutil
import random
import yaml
from collections import defaultdict
from ultralytics import YOLO

def prepare_subset(base_dir, num_train=120, num_val=30):
    random.seed(42)
    train_img_dir = os.path.join(base_dir, 'images', 'train')
    train_lbl_dir = os.path.join(base_dir, 'labels', 'train')
    val_img_dir = os.path.join(base_dir, 'images', 'val')
    val_lbl_dir = os.path.join(base_dir, 'labels', 'val')

    subset_dir = os.path.join(base_dir, 'subset_split')
    os.makedirs(os.path.join(subset_dir, 'images', 'train'), exist_ok=True)
    os.makedirs(os.path.join(subset_dir, 'images', 'val'), exist_ok=True)
    os.makedirs(os.path.join(subset_dir, 'labels', 'train'), exist_ok=True)
    os.makedirs(os.path.join(subset_dir, 'labels', 'val'), exist_ok=True)

    # Class indexing
    class_to_files = defaultdict(list)
    for f in os.listdir(train_lbl_dir):
        if not f.endswith('.txt'):
            continue
        base_name = f[:-4]
        img_name = f"{base_name}.jpg"
        if not os.path.exists(os.path.join(train_img_dir, img_name)):
            continue
        with open(os.path.join(train_lbl_dir, f)) as fp:
            classes = set()
            for line in fp:
                p = line.strip().split()
                if p:
                    classes.add(int(p[0]))
            for c in classes:
                class_to_files[c].append(base_name)

    # Prioritize rare classes
    selected_train = set()
    for c in [6, 7, 3, 4, 5, 0, 1, 2]:
        files = class_to_files[c]
        random.shuffle(files)
        selected_train.update(files[:20])

    selected_train = list(selected_train)[:num_train]

    # Copy train files
    for name in selected_train:
        shutil.copy2(os.path.join(train_img_dir, f"{name}.jpg"), os.path.join(subset_dir, 'images', 'train', f"{name}.jpg"))
        shutil.copy2(os.path.join(train_lbl_dir, f"{name}.txt"), os.path.join(subset_dir, 'labels', 'train', f"{name}.txt"))

    # Val files
    val_files = [f[:-4] for f in os.listdir(val_lbl_dir) if f.endswith('.txt')][:num_val]
    for name in val_files:
        val_img = os.path.join(val_img_dir, f"{name}.jpg")
        val_lbl = os.path.join(val_lbl_dir, f"{name}.txt")
        if os.path.exists(val_img) and os.path.exists(val_lbl):
            shutil.copy2(val_img, os.path.join(subset_dir, 'images', 'val', f"{name}.jpg"))
            shutil.copy2(val_lbl, os.path.join(subset_dir, 'labels', 'val', f"{name}.txt"))

    yaml_path = os.path.join(subset_dir, 'subset.yaml')
    yaml_data = {
        'path': os.path.abspath(subset_dir),
        'train': 'images/train',
        'val': 'images/val',
        'nc': 8,
        'names': ['handrise', 'look_forward', 'read', 'sleep', 'stand', 'turn_head', 'using_device', 'write']
    }
    with open(yaml_path, 'w') as fp:
        yaml.dump(yaml_data, fp)

    print(f"Prepared subset at: {subset_dir}")
    print(f"Train samples: {len(selected_train)}, Val samples: {len(val_files)}")
    return yaml_path

def train_model():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DATASET FROM KAGEL'))
    yaml_path = prepare_subset(base_dir, num_train=80, num_val=20)

    # Base pretrained model
    pretrained_weights = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'BOOTCAMP ON AI_Practicals', 'yolov8n.pt'))
    if not os.path.exists(pretrained_weights):
        pretrained_weights = 'yolov8n.pt'

    print(f"Loading pretrained model from: {pretrained_weights}")
    model = YOLO(pretrained_weights)

    # Train for 2 epochs on CPU (fast convergence for demo and production readiness)
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'runs'))
    print("Beginning model training on Classroom Behavior Dataset...")
    results = model.train(
        data=yaml_path,
        epochs=2,
        imgsz=320,
        batch=16,
        device='cpu',
        project=output_dir,
        name='classroom_behavior',
        exist_ok=True,
        verbose=True
    )

    # Save to final model destination
    final_model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'classroom_behavior_yolov8.pt'))
    best_weights = os.path.join(output_dir, 'classroom_behavior', 'weights', 'best.pt')
    if os.path.exists(best_weights):
        shutil.copy2(best_weights, final_model_path)
    else:
        last_weights = os.path.join(output_dir, 'classroom_behavior', 'weights', 'last.pt')
        if os.path.exists(last_weights):
            shutil.copy2(last_weights, final_model_path)
        else:
            model.save(final_model_path)

    print(f"\nModel training complete! Final model saved to: {final_model_path}")
    return final_model_path

if __name__ == '__main__':
    train_model()
