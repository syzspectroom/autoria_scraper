# Autoria Scraper 🚗📊

A powerful vehicle data collection toolkit that scrapes car listings, downloads images, and validates them using AI. Fast, efficient, and highly customizable.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-scrapy%2Crequests%2Cultralytics%2Ctorch-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Features ✨

- 🕸️ Web scraping of vehicle listings from auto.ria.com
- 🔍 Collection of detailed vehicle specifications
- 📁 Organized data storage structure
- 🖼️ Automated image downloading with smart rate limiting
- 🤖 AI-powered image validation using YOLOv8 models
- 📊 Vehicle metadata processing and matching

## Data Collection Pipeline 🔄

1. **Scrape** - Extract vehicle listings and specifications
2. **Process** - Match and enrich vehicle metadata
3. **Download** - Collect vehicle images
4. **Validate** - Filter using AI object detection/classification
5. **Analyze** - Work with clean, validated vehicle data

## Installation 📦

```bash
# Clone repository
git clone https://github.com/syzspectroom/autoria_scraper
cd autoria_scraper

# Install dependencies
pip install scrapy
pip install requests tqdm ratelimit
pip install ultralytics torch torchvision tqdm Pillow opencv-python
```

## Project Structure

```bash
car-scraper/
├── car_scraper/               # Main Scrapy project directory
│   ├── spiders/               # Scrapy spiders
│   │   ├── car_spider.py      # Spider for auto.ria.com
│   ├── items.py               # Data structure definitions
│   ├── pipelines.py           # Data processing pipelines
│   └── settings.py            # Scrapy settings
├── data/                      # Data storage directory
│   ├── pictures/              # Downloaded vehicle images
│   ├── valid_pictures/        # Validated vehicle images
│   ├── invalid_pictures/      # Invalid images
│   └── vehicle_models/        # Vehicle model data
├── download_vehicle_data.py   # Script to download vehicle metadata
├── process_vehicles.py        # Script to process and match vehicle data
├── download_images.py         # Script to download vehicle images
├── check_images_detect.py     # YOLOv8 detection-based image validation
├── check_images_classify.py   # YOLOv8 classification-based image validation
├── reset_detection_state.py   # Reset image validation results
└── run_spider.py              # Helper script to run the spider
```

## Usage 🚀

### Complete Workflow

```bash
# 1. Scrape vehicle listings
scrapy crawl CarSpider -o data/cars.json
# OR
python run_spider.py

# 2. Download vehicle metadata
python download_vehicle_data.py

# 3. Process vehicle data
python process_vehicles.py

# 4. Download vehicle images
python download_images.py

# 5. Validate images (choose one method)
python check_images_detect.py   # Using object detection
# OR
python check_images_classify.py # Using classification

# 6. Reset validation (if needed)
python reset_detection_state.py
```

## Components 🧩

### Web Scraping 🕸️

- Extracts vehicle ID, brand, model, year
- Captures price, location, fuel type
- Collects technical specifications
- Finds high-quality image URLs

### Vehicle Metadata 📋

- Downloads comprehensive brand/model data
- Organizes into structured JSON format
- Supports multiple vehicle categories

### Image Processing 🖼️

- Intelligent folder structure by vehicle ID
- Rate-limited downloading to avoid IP blocks
- AI-powered validation (YOLOv8)

## Disclaimer ⚠️

- Web scraping may violate terms of service
- Always respect robots.txt and rate limits
- This tool is for educational purposes only
- Use responsibly and ethically

## Contributing 🤝

Found a bug? Open an issue! Want to add features? Submit a PR!
The project is open to enhancements and additional data sources.
