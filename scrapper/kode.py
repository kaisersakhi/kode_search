import scrapy
import json
from models.models import ApplicationModel, Domain, Url, FileQueue
from kode_config import KodeConfig
import time
from urllib.parse import urlparse
import json
import os
import trafilatura as trafil
from pathlib import Path
import re
from scrapy.crawler import CrawlerProcess

class KodeSpider(scrapy.Spider):
    name = "kode"
    allowed_domains = ["kode.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,  # Increase parallel requests
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 0.25,  # Delay between each request
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
    }

    def __init__(self):
        self.pwd = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(self.pwd, "domains.json"), "r") as file:
            data = json.load(file)
            self.start_urls = data["start_urls"]
            self.allowed_domains = data["allowed_domains"]

        # Connect Database
        ApplicationModel.database.connect()
        ApplicationModel.database.create_tables([Domain, Url, FileQueue], safe=True)

        self.data_dir = KodeConfig.get("shared_data_path")
        super().__init__()


    def parse(self, response):
        # Return if Url has already been processed.
        # import pdb; pdb.set_trace()

        if url_visited_before(response):
            return
        
        # Sleep before proceeding further.
        time.sleep(1)
        timestamp = int(time.time())

        create_dirs_for(current_domain(response))

        title = "_".join(response.url.split("/")[3:]) + f"-{timestamp}"

        json_file_name = get_file_name(current_domain(response), title, extension="json")
        html_file_name = get_file_name(current_domain(response), title, extension="html")

        json_body = get_json_content(response, timestamp, title, html_file_name)

        write_to_fs(response.body.decode("UTF-8", errors="ignore"), html_file_name)
        write_to_fs(json.dumps(json_body), json_file_name)

        created_url = Url.create(
            title = title,
            uri = response.url,
            html_file_path = html_file_name,
            domain = create_or_first_domain(response)
        )

        FileQueue.create(
            url=created_url,
            path=json_file_name,
        )

        for path in get_page_paths(response):
            fully_qualified_url = enqueueable_link(response, path)

            if fully_qualified_url:
                print(f"Added {fully_qualified_url} to the frontier queue.")
        
                yield scrapy.Request(fully_qualified_url, callback=self.parse)


def create_dirs_for(current_domain):
    os.makedirs(os.path.join(KodeConfig.get("shared_data_path"), current_domain), exist_ok=True)
    os.makedirs(os.path.join(KodeConfig.get("shared_data_path"), current_domain, "html_files"), exist_ok=True)
    os.makedirs(os.path.join(KodeConfig.get("shared_data_path"), current_domain, "json_files"), exist_ok=True)

def get_file_name(current_domain, title, extension):
    sub_dir = "html_files" if extension == "html" else "json_files"
    return str(os.path.join(current_domain, sub_dir, f"{title}.{extension}"))

def get_json_content(response, ts, title, html_file_name):
    # import pdb; pdb.set_trace()
    json_str = trafil.extract(response.body, output_format="json")
    json_body = json.loads(json_str)

    json_body["title"] = title
    json_body["timestamp"] = ts
    json_body["url"] = response.url
    json_body["html_source"] = html_file_name

    return json_body


def write_to_fs(content, file_name):
    full_path = os.path.join(KodeConfig.get("shared_data_path"), file_name)
    Path(full_path).write_text(content)

def get_page_paths(response):
    return response.xpath("//a/@href").extract()

def create_or_first_domain(response):
    domain, _ = Domain.get_or_create(name=current_domain(response))
    return domain

def current_domain(response):
    return response.url.split("/")[2]

def enqueueable_link(response, path):
    enqueuable = ""
    # import pdb; pdb.set_trace()

    # If path is a relative path.
    if not (bool(urlparse(path).scheme) and bool(urlparse(path).netloc)) and is_enqueable(response.urljoin(path)):
        enqueuable = response.urljoin(path)
        # If link is absolute path, then check if the base url is same and the path is enqueueble
    elif urlparse(response.url).netloc == urlparse(path).netloc and is_enqueable(path):
        enqueuable = path

    return enqueuable

def is_enqueable(link):
    #  only donwnload those webpage that have following keywords in thme:
    # docs, doc, documentation, documentations, user_guide, guide, user_guides, instructions, 
    pattern = r'\b(docs|doc|documentation|documentations|user_guide|guide|guides|user_guides|instructions|help|manual|how-to|tutorials|tutorial|references|reference|faq|api|support|kb|)\b'
    if re.search(pattern, link):
        return True
    return False

def url_visited_before(response):
    domains = Domain.select().where(Domain.name==current_domain)
    
    # Only 10000 pages should be scrapped from a specific domain.
    if domains.count() > 0 and domains[0].urls.count() > 10000:
        return True

    return Url.select().where(Url.uri==response.url).count() > 0
