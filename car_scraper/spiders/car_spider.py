import scrapy
import re
from car_scraper.items import CarItem

class CarSpiderSpider(scrapy.Spider):
    name = "CarSpider"
    allowed_domains = ['auto.ria.com']
    start_urls = ["https://auto.ria.com/car/used/"]


    def parse(self, response):
        for content in response.css('div.content-bar'):
            car = CarItem()
            car['URL'] = content.css('a.address').attrib['href']
            idMatch = re.search(r'_(\d+)\.html$', car['URL'])
            if idMatch:
                car['ID'] = int(idMatch.group(1))
            car['Title'] = content.css('span.blue.bold::text').get().strip()
            car['Price'] = content.css('span.bold.size22.green::text').get().replace(" ", "")
            car['Mileage'] = content.css('li.item-char.js-race::text').get().replace(' тис. км', '').strip()

            # Location extraction
            location = content.xpath('.//li[contains(@class, "js-location")]/i[@class="icon-location"]/following-sibling::text()').get()
            if location:
                car['Location'] = location.strip()
            else:
                car['Location'] = None

            # Add some debugging output
            self.logger.debug(f"Location: {car['Location']}")
                
            # Extract fuel type for both fuel-powered and electric cars
            fuel_type_nodes = content.xpath('.//li[i[contains(@class, "icon-fuel") or contains(@class, "icon-battery")]]/text()').extract()

            fuel_type = next((node.strip() for node in fuel_type_nodes if node.strip()), None)

            print(f"Cleaned fuel type: {fuel_type}")  # Debug print

            if fuel_type:
                # Handle different formats
                if ',' in fuel_type:
                    # For fuel-powered cars with engine volume
                    fuel_parts = fuel_type.split(',')
                    car['FuelType'] = fuel_parts[0].strip()
                    car['EngineVolume'] = fuel_parts[1].strip() if len(fuel_parts) > 1 else None
                else:
                    # For electric cars or fuel types without engine volume
                    car['FuelType'] = fuel_type
                    car['EngineVolume'] = None
            else:
                car['FuelType'] = None
                car['EngineVolume'] = None

# Add some debugging output
            self.logger.debug(f"Fuel Type: {car['FuelType']}, Engine Volume: {car['EngineVolume']}")

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
            gearbox = next((node.strip() for node in gearbox_nodes if node.strip()), None)
            car['Gearbox'] = gearbox

            car['ImageURL'] = content.css('picture img::attr(src)').get()

            yield car
        next_page = response.css('a.page-link.js-next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
