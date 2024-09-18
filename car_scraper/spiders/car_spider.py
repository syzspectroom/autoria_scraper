import scrapy
import re
from car_scraper.items import CarItem

class CarSpiderSpider(scrapy.Spider):
    name = "CarSpider"
    allowed_domains = ['auto.ria.com']
    start_urls = ["https://auto.ria.com/car/used/"]

    def parse(self, response):
        for content in response.xpath('//section[contains(@class, "ticket-item")]'):
        # for content in response.css('div.content-bar'):
            car = CarItem()
            
            # Extract data from data attributes
            data_div = content.xpath('.//div[@data-advertisement-data]')
            car['ID'] = data_div.xpath('@data-id').get('')
            car['URL'] = 'https://auto.ria.com' + data_div.xpath('@data-link-to-view').get('')
            car['Brand'] = data_div.xpath('@data-mark-name').get('')
            car['Model'] = data_div.xpath('@data-model-name').get('')
            car['Year'] = data_div.xpath('@data-year').get('')

            # Extract other details
            car['Title'] = content.css('span.blue.bold::text').get('').strip()
            car['Price'] = content.css('span.bold.size22.green::text').get('').replace(" ", "")
            car['Mileage'] = content.css('li.item-char.js-race::text').get('').replace(' тис. км', '000').strip()

            # Location extraction
            location = content.xpath('.//li[contains(@class, "js-location")]/i[@class="icon-location"]/following-sibling::text()').get()
            car['Location'] = location.strip() if location else None

            # Extract fuel type and engine volume
            fuel_type_nodes = content.xpath('.//li[i[contains(@class, "icon-fuel") or contains(@class, "icon-battery")]]/text()').extract()
            fuel_type = next((node.strip() for node in fuel_type_nodes if node.strip()), None)

            if fuel_type:
                if ',' in fuel_type:
                    fuel_parts = fuel_type.split(',')
                    car['FuelType'] = fuel_parts[0].strip()
                    car['EngineVolume'] = fuel_parts[1].strip() if len(fuel_parts) > 1 else None
                else:
                    car['FuelType'] = fuel_type
                    car['EngineVolume'] = None
            else:
                car['FuelType'] = None
                car['EngineVolume'] = None

            # Extract generation, engine powertrain, and trim
            generation_text = ' '.join(text.strip() for text in content.css('div.generation ::text').getall() if text.strip())
            if generation_text:
                parts = generation_text.split(' • ')
                car['Generation'] = parts[0] if parts else None
                car['Trim'] = parts[-1] if len(parts) > 1 else None
                car['EnginePowertrain'] = ' • '.join(parts[1:-1]) if len(parts) > 2 else None
            else:
                car['Generation'] = None
                car['EnginePowertrain'] = None
                car['Trim'] = None

            # Gearbox extraction
            gearbox_nodes = content.xpath('.//li[i[contains(@class, "icon-akp") or contains(@class, "icon-transmission")]]/text()').extract()
            car['Gearbox'] = next((node.strip() for node in gearbox_nodes if node.strip()), None)

            car['ImageURL'] = content.css('picture img::attr(src)').get()

            # Debugging output
            self.logger.debug(f"Location: {car['Location']}")
            self.logger.debug(f"Fuel Type: {car['FuelType']}, Engine Volume: {car['EngineVolume']}")
            self.logger.debug(f"Gearbox: {car['Gearbox']}")

            yield car

        next_page = response.css('a.page-link.js-next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
