import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ultralytics import YOLO
import cv2
import torch
import traceback

# Load YOLOv8 model
model = YOLO('yolov8s.pt')

def validate_image(image_path, valid_dir, invalid_dir):
    try:
        # Read image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to read image: {image_path}")

        # Run inference
        results = model(img)
        
        # Check if 'car' is detected with confidence > 0.3
        car_detected = any(result.boxes.cls[result.boxes.cls == 2].numel() > 0 and 
                           result.boxes.conf[result.boxes.cls == 2].max() > 0.3 
                           for result in results)
        
        # Move the image to the appropriate directory
        new_path = os.path.join(valid_dir if car_detected else invalid_dir, os.path.basename(image_path))
        shutil.move(image_path, new_path)
        
        return car_detected, new_path
    except Exception as e:
        error_msg = f"Error processing image {image_path}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open('error_log.txt', 'a') as f:
            f.write(error_msg + '\n\n')
        return False, image_path

def process_images(root_dir='data/pictures', valid_dir='data/valid_pictures', invalid_dir='data/invalid_pictures'):
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)
    
    image_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
    
    valid_count = 0
    invalid_count = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:  # Increased back to 20 for better performance
        futures = [executor.submit(validate_image, path, valid_dir, invalid_dir) for path in image_paths]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Validating images"):
            is_valid, new_path = future.result()
            if is_valid:
                valid_count += 1
                print(f"Moved valid image to: {new_path}")
            else:
                invalid_count += 1
                print(f"Moved invalid image to: {new_path}")
    
    return valid_count, invalid_count

if __name__ == "__main__":
    # Set the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Move model to the appropriate device
    model.to(device)
    
    valid, invalid = process_images()
    print(f"Validation complete.")
    print(f"Valid images: {valid}")
    print(f"Invalid images: {invalid}")
