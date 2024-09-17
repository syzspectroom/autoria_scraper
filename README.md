# CAR SCRAPER

install scrapy:

```bash
pip install scrapy
```

```bash
pip install requests tqdm ratelimit
```

```bash
pip install ultralytics torch torchvision tqdm Pillow
```

run:

```bash
scrapy crawl CarSpider -o data/cars.json

```

1. scrapy crawl CarSpider -o data/cars.json
2. download_vehicle_data.py
3. process_vehicles.py
4. download_images.py
5. check_images_detect.py or check_images_classify.py
