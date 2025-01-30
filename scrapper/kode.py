import scrapy
import json

class KodeSpider(scrapy.Spider):
    name = "kode"
    allowed_domains = ["kode.com"]

    def __init__(self):
        with open("./domains.json", "r") as file:
            data = json.load(file)
            self.start_urls = data["links"]
            self.allowed_domains = self.start_urls
        super().__init__()


    def parse(self, response):
        print(self.start_urls)
        pass
