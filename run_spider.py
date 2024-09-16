from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from car_scraper.spiders.car_spider import CarSpiderSpider

def run_spider():
    settings = get_project_settings()
    settings.set('JOBDIR', 'crawls/auto_ria_job')
    process = CrawlerProcess(settings)
    process.crawl(CarSpiderSpider)
    process.start()

if __name__ == '__main__':
    run_spider()
