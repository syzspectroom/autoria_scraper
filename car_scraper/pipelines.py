import json
from itemadapter import ItemAdapter

class CarScraperPipeline:
    def __init__(self):
        self.file = open('cars.json', 'w')
        self.file.write('[\n')
        self.first_item = True

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        else:
            self.first_item = False
        
        line = json.dumps(ItemAdapter(item).asdict())
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
