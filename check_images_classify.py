import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ultralytics import YOLO
import cv2
import torch
import traceback

# Load YOLOv8 classification model
model = YOLO('yolov8m-cls.pt')

# List of car-related classes from ImageNet
car_classes = {
    436: 'beach_wagon, station_wagon, wagon, estate_car, beach_waggon, station_waggon, waggon',
    511: 'convertible',
    581: 'grille, radiator grille',
    609: 'jeep, landrover',
    627: 'limousine, limo',
    656: 'minivan',
    705: 'passenger_car, coach, carriage',
    717: 'pickup, pickup_truck',
    751: 'racer, race_car, racing_car',
    817: 'sports_car, sport_car',
    864: 'tow_truck, tow_car, wrecker',
    867: 'trailer_truck, tractor_trailer, trucking_rig, rig, articulated_lorry, semi',
}

def validate_image(image_path, valid_dir, invalid_dir):
    try:
        # Read image using OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Unable to read image: {image_path}")

        # Run inference
        results = model(img)[0]
        
        # Get the top predicted class and its confidence
        top_pred = results.probs.top1
        confidence = results.probs.top1conf.item()
        class_name = results.names[top_pred]
        
        # Check if the predicted class is in our list of car classes
        car_detected = top_pred in car_classes and confidence > 0.19
        
        # Create the same subfolder structure in valid or invalid directory
        rel_path = os.path.relpath(image_path, 'data/pictures')
        new_dir = os.path.join(valid_dir if car_detected else invalid_dir, os.path.dirname(rel_path))
        os.makedirs(new_dir, exist_ok=True)
        
        # Move the image to the appropriate directory
        new_path = os.path.join(new_dir, os.path.basename(image_path))
        shutil.move(image_path, new_path)
        
        print(f"Image: {image_path}, Class: {class_name}, Confidence: {confidence:.2f}, Car detected: {car_detected}")
        
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
    
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(validate_image, path, valid_dir, invalid_dir) for path in image_paths]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Validating images"):
            is_valid, new_path = future.result()
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
    
    # Clean up empty directories
    cleanup_empty_dirs(root_dir)
    
    return valid_count, invalid_count

def cleanup_empty_dirs(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # check if directory is empty
                os.rmdir(dir_path)
                print(f"Removed empty directory: {dir_path}")

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model.to(device)
    
    valid, invalid = process_images()
    print(f"Validation complete.")
    print(f"Valid images: {valid}")
    print(f"Invalid images: {invalid}")
