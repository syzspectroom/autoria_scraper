BOT_NAME = "car_scraper"

SPIDER_MODULES = ["car_scraper.spiders"]
NEWSPIDER_MODULE = "car_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
ITEM_PIPELINES = {
   "car_scraper.pipelines.CarScraperPipeline": 300,
}

DOWNLOAD_DELAY = 1
# RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
