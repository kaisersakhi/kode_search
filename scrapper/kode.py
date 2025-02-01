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

class KodeSpider(scrapy.Spider):
    name = "kode"
    allowed_domains = ["kode.com"]

    def __init__(self):
        with open("./domains.json", "r") as file:
            data = json.load(file)
            self.start_urls = data["links"]
            self.allowed_domains = self.start_urls

        # Connect Database
        ApplicationModel.database.connect()
        ApplicationModel.database.create_tables([Domain, Url, FileQueue], safe=True)

        self.data_dir = KodeConfig.data_path
        super().__init__()


    def parse(self, response):
        # Return if Url has already been processed.
        if Url.select().where(Url.uri == response.url)[0] or Domain.get(name=current_domain(response)).urls.count() > 1000:
            return
        
        # Sleep before proceeding further.
        time.sleep(2)
        timestamp = time.time()

        create_dirs_for(current_domain(response))

        title = "_".join(response.url.split("/")[3:]) + f"-{timestamp}"

        json_file_name = get_file_name(current_domain(response), title, extension="json")
        html_file_name = get_file_name(current_domain(response), title, extension="html")

        json_body = get_json_content(response, timestamp, title, html_file_name)

        write_to_fs(response.body.decode("UTF-8", errors="ignore"), html_file_name)
        write_to_fs(json.dumps(json_body), json_file_name)

        path = get_page_paths(response)

        Url.create(
            title = title,
            uri = response.url,
            html_file_path = html_file_name,
            domain = create_or_first_domain(response)
        )


def create_dirs_for(current_domain):
    os.makedirs(os.path.join(KodeConfig.data_path, current_domain), exist_ok=True)
    os.makedirs(os.path.join(KodeConfig.data_path, current_domain, "html_files"), exist_ok=True)
    os.makedirs(os.path.join(KodeConfig.data_path, current_domain, "json_files"), exist_ok=True)

def get_file_name(current_domain, title, extension):
    sub_dir = "html_files" if extension == "html" else "json_files"
    return str(os.path.join(KodeConfig.data_path, current_domain, sub_dir, f"{title}.{extension}"))

def get_json_content(response, ts, title, html_file_name):
    json_str = trafil.extract(response.body, output_format="json")
    json_body = json.loads(json_str)

    json_body["id"] = f"id:kode_app:kode_app::{title}"
    json_body["timestamp"] = ts
    json_body["url"] = response.url
    json_body["html_source"] = html_file_name

    return json_body


def write_to_fs(content, file_name):
    Path(file_name).write_text(content)

def get_page_paths(response):
    response.extract("//a/@href").extract()

def create_or_first_domain(response):
    domain, _ = Domain.get_or_create(name=current_domain(response))
    return domain

def current_domain(response):
    return response.url.split("/")[2]