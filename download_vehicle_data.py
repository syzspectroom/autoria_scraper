import requests
import json
import os
import time
import re

def sanitize_filename(filename):
    # Convert to lowercase and replace spaces with underscores
    sanitized = filename.lower().replace(' ', '_')
    # Remove or replace other special characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', sanitized)
    # Remove leading/trailing periods and spaces
    sanitized = sanitized.strip('. ')
    return sanitized if sanitized else 'unnamed'

def download_and_save_json(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Downloaded and saved: {filename}")
        return data
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {url}")
    except IOError as e:
        print(f"Error writing file {filename}: {e}")
    return None

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filename}")
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return None

def file_exists(filename):
    return os.path.isfile(filename)

def main():
    categories = {1: "passenger_car", 7: "bus"}
    brands_file = "data/car_brands.json"
    models_dir = "data/vehicle_models"

    os.makedirs(models_dir, exist_ok=True)

    all_brands = {}

    for category, category_name in categories.items():
        brands_url = f"https://auto.ria.com/demo/api/categories/{category}/brands/_active/_with_count/_with_country?langId=4"
        category_brands_file = f"data/{category_name}_brands.json"

        if not file_exists(category_brands_file):
            brands_data = download_and_save_json(brands_url, category_brands_file)
        else:
            print(f"Using existing file: {category_brands_file}")
            brands_data = load_json(category_brands_file)

        if not brands_data:
            continue

        for brand in brands_data:
            brand_value = brand.get('value')
            brand_name = brand.get('name')
            if brand_value and brand_name:
                if brand_name not in all_brands:
                    all_brands[brand_name] = {"value": brand_value, "categories": []}
                all_brands[brand_name]["categories"].append(category_name)

                models_url = f"https://auto.ria.com/api/categories/{category}/marks/{brand_value}/models/_active/_with_count?langId=4"
                sanitized_brand_name = sanitize_filename(brand_name)
                models_file = os.path.join(models_dir, f"{sanitized_brand_name}_{category_name}_models.json")
                
                if file_exists(models_file):
                    print(f"Skipping existing file: {models_file}")
                    models_data = load_json(models_file)
                else:
                    models_data = download_and_save_json(models_url, models_file)
                    time.sleep(1)  # Delay to avoid overloading the server

                if models_data:
                    for model in models_data:
                        model['vehicle_type'] = category_name

    # Save the combined brands data
    with open(brands_file, 'w', encoding='utf-8') as f:
        json.dump(all_brands, f, ensure_ascii=False, indent=2)
    print(f"Combined brands data saved to: {brands_file}")

if __name__ == "__main__":
    main()
