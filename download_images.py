import json
import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=1)
def download_image(car):
    try:
        car_id = car['ID']
        image_url = car['ImageURL']
        
        # Correctly modify URL to get HD version
        hd_image_url = re.sub(r'(\w{2})\.jpg$', r'hd.jpg', image_url)
        
        folder_path = f'data/pictures/{car_id}'
        os.makedirs(folder_path, exist_ok=True)
        
        response = requests.get(hd_image_url)
        response.raise_for_status()
        
        file_name = os.path.join(folder_path, f"{car_id}.jpg")
        with open(file_name, 'wb') as file:
            file.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading image for car ID {car_id}: {str(e)}")
        return False

def main():
    with open('cars.json', 'r') as file:
        cars = json.load(file)
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(download_image, car) for car in cars]
        
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Downloading images"):
            pass

    successful = sum(1 for future in futures if future.result())
    print(f"Downloaded {successful} out of {len(cars)} images successfully.")

if __name__ == "__main__":
    main()
