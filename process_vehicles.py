import json
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sanitize_filename(filename):
    sanitized = filename.lower().replace(' ', '_')
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', sanitized)
    sanitized = sanitized.strip('. ')
    return sanitized if sanitized else 'unnamed'

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {filename}")
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
    return None

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_matching_brand(title, brands):
    if not title:
        return None, None
    title_words = title.lower().split()
    for brand_name, brand_info in brands.items():
        if (title_words and brand_name.lower() == title_words[0]) or f"{brand_name.lower()} " in title.lower():
            return brand_name, brand_info
    return None, None

def find_matching_model(title, models):
    title_words = set(title.lower().split())
    best_match = None
    max_words_matched = 0

    for model in models:
        model_name = model['name'].lower()
        model_words = set(model_name.split())
        words_matched = len(title_words.intersection(model_words))

        if words_matched > max_words_matched:
            max_words_matched = words_matched
            best_match = model

    return best_match

def main():
    cars_file = "data/cars.json"
    brands_file = "data/car_brands.json"
    models_dir = "data/vehicle_models"
    output_file = "data/cars_with_brands_and_models.json"

    cars = load_json(cars_file)
    brands = load_json(brands_file)

    if not cars or not brands:
        return

    total_count = len(cars)
    unknown_brand_count = 0
    unknown_model_count = 0
    missing_fields_count = 0

    for car in cars:
        if 'Title' not in car or not car['Title']:
            logging.error(f"Missing or empty 'Title' field in car entry: {car}")
            missing_fields_count += 1
            continue

        title = car['Title']
        matching_brand, brand_info = find_matching_brand(title, brands)

        if matching_brand:
            car['Brand'] = matching_brand
            
            # Try to find matching model
            model_found = False
            for category in ['passenger_car', 'bus']:
                brand_models_file = os.path.join(models_dir, f"{sanitize_filename(matching_brand)}_{category}_models.json")
                if os.path.exists(brand_models_file):
                    brand_models = load_json(brand_models_file)
                    if brand_models:
                        matching_model = find_matching_model(title, brand_models)
                        if matching_model:
                            car['Model'] = matching_model['name']
                            car['VehicleType'] = category
                            model_found = True
                            break

            if not model_found:
                car['Model'] = 'Unknown'
                car['VehicleType'] = 'Unknown'
                unknown_model_count += 1
                logging.warning(f"No matching model found for: {title} (Brand: {matching_brand})")
        else:
            car['Brand'] = 'Unknown'
            car['Model'] = 'Unknown'
            car['VehicleType'] = 'Unknown'
            unknown_brand_count += 1
            id_info = f"(ID: {car['ID']})" if 'ID' in car else "(ID: Missing)"
            logging.warning(f"Unknown brand for vehicle: {title} {id_info}")

    save_json(cars, output_file)
    
    # Log summary
    logging.info(f"Processing complete. Total vehicles: {total_count}")
    logging.info(f"Vehicles with known brands: {total_count - unknown_brand_count - missing_fields_count}")
    logging.info(f"Vehicles with unknown brands: {unknown_brand_count}")
    logging.info(f"Vehicles with unknown models: {unknown_model_count}")
    logging.info(f"Vehicles with missing fields: {missing_fields_count}")
    logging.info(f"Percentage of unknown brands: {(unknown_brand_count / total_count) * 100:.2f}%")
    logging.info(f"Percentage of unknown models: {(unknown_model_count / total_count) * 100:.2f}%")
    logging.info(f"Updated vehicle data saved to '{output_file}'")

if __name__ == "__main__":
    main()
