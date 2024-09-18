import json
import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ratelimit import limits, sleep_and_retry
import time

def get_folder_path(car_id):
    car_id = str(car_id).zfill(8)
    return os.path.join('data', 'pictures', car_id[:2], car_id[2:4], car_id[4:6])

@sleep_and_retry
@limits(calls=20, period=1)
def download_image(car):
    car_id = car.get('ID')
    if not car_id:
        return False, "no_id"
    
    image_url = car.get('ImageURL')
    if not image_url:
        return False, "no_url"

    folder_path = get_folder_path(car_id)
    file_name = os.path.join(folder_path, f"{car_id}.jpg")
    
    if os.path.exists(file_name):
        return True, "exists"

    os.makedirs(folder_path, exist_ok=True)

    def try_download(url_suffix):
        try:
            modified_url = re.sub(r'(\w{2})\.jpg$', f'{url_suffix}.jpg', image_url)
            response = requests.get(modified_url)
            response.raise_for_status()
            
            with open(file_name, 'wb') as file:
                file.write(response.content)
            
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                return False
            raise
        except Exception as e:
            print(f"Error downloading image for car ID {car_id}: {str(e)}")
            return False

    if try_download('hd') or try_download('f'):
        return True, "downloaded"
    
    return False, "failed"

def batch_check_existence(cars, batch_size=1000):
    existing_files = set()
    skipped_cars = 0
    for i in range(0, len(cars), batch_size):
        batch = cars[i:i+batch_size]
        for car in batch:
            car_id = car.get('ID')
            if car_id:
                file_path = os.path.join(get_folder_path(car_id), f"{car_id}.jpg")
                if os.path.exists(file_path):
                    existing_files.add(file_path)
            else:
                skipped_cars += 1
    return existing_files, skipped_cars

def main():
    start_time = time.time()

    try:
        with open('data/cars_with_brands_and_models.json', 'r') as file:
            cars = json.load(file)
        
        json_load_time = time.time()
        print(f"JSON loading time: {json_load_time - start_time:.2f} seconds")

        # Debug: Print the first few car objects
        print("Sample car data:")
        for i, car in enumerate(cars[:5]):
            print(f"Car {i + 1}: {car}")

        # eligible_cars = [car for car in cars if car.get('VehicleType', '').lower() != 'unknown']
        eligible_cars = cars 
        filtering_time = time.time()
        print(f"Filtering time: {filtering_time - json_load_time:.2f} seconds")

        existing_files, skipped_cars = batch_check_existence(eligible_cars)
        
        existence_check_time = time.time()
        print(f"Batch existence check time: {existence_check_time - filtering_time:.2f} seconds")
        print(f"Skipped {skipped_cars} cars due to missing ID")

        cars_to_download = [car for car in eligible_cars if car.get('ID') and os.path.join(get_folder_path(car['ID']), f"{car['ID']}.jpg") not in existing_files]

        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = [executor.submit(download_image, car) for car in cars_to_download]
            
            results = list(tqdm(as_completed(futures), total=len(futures), desc="Downloading images"))

        download_time = time.time()
        print(f"Download time: {download_time - existence_check_time:.2f} seconds")

        result_counts = {'downloaded': 0, 'exists': 0, 'failed': 0, 'no_id': 0, 'no_url': 0}
        for future in results:
            _, status = future.result()
            result_counts[status] += 1

        print(f"Download results: {result_counts}")
        print(f"Skipped {len(eligible_cars) - len(cars_to_download)} existing images.")
        print(f"Skipped {len(cars) - len(eligible_cars)} cars with Unknown VehicleType.")

        print(f"Total execution time: {time.time() - start_time:.2f} seconds")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
