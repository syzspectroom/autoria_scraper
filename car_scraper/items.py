import scrapy

class CarItem(scrapy.Item):
    ID = scrapy.Field()
    URL = scrapy.Field()
    Title = scrapy.Field()
    Price = scrapy.Field()
    Location = scrapy.Field()
    Mileage = scrapy.Field()
    Generation = scrapy.Field()
    EnginePowertrain = scrapy.Field()
    Trim = scrapy.Field()
    FuelType = scrapy.Field()
    EngineVolume = scrapy.Field()
    Gearbox = scrapy.Field()
    ImageURL = scrapy.Field()   
