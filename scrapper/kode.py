import scrapy
import json
from models.models import ApplicationModel, Domain, Url, FileQueue
from kode_config import KodeConfig
import time
from urllib.parse import urlparse
import os
import trafilatura as trafil
from pathlib import Path
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import math


class KodeSpider(scrapy.Spider):
    name = "kode"
    allowed_domains = []
    start_urls = []

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("CONCURRENT_REQUESTS", 32, priority="spider")
        # settings.set("CONCURRENT_REQUESTS_PER_DOMAIN", 2, priority="spider")
        settings.set("REDIRECT_MAX_TIMES", 3, priority="spider")
        settings.set("AUTOTHROTTLE_ENABLED", True, priority="spider")
        settings.set("PROXY_POOL_ENABLED", True, priority="spider")
        settings.set("DOWNLOADER_MIDDLEWARES", {
            # 'scrapy_proxy_pool.middlewares.ProxyPoolMiddleware': 610,
            # 'scrapy_proxy_pool.middlewares.BanDetectionMiddleware': 620,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
        }, priority="spider")
        settings.set("LOG_LEVEL", "WARN")
        settings.set("USER_AGENTS", [
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/57.0.2987.110 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/61.0.3163.79 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
            'Gecko/20100101 '
            'Firefox/55.0'),  # firefox
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/61.0.3163.91 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/62.0.3202.89 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/63.0.3239.108 '
            'Safari/537.36'),  # chrome
        ])

    def __init__(self, urls=None, *args, **kwargs):
        self.pwd = os.path.dirname(os.path.abspath(__file__))
        self.start_urls = urls.split()
        with open(os.path.join(self.pwd, "domains.json"), "r") as file:
            data = json.load(file)
            # self.start_urls = data["start_urls"]
            self.allowed_domains = data["allowed_domains"]

        self.data_dir = KodeConfig.get("shared_data_path")

        #     # Connect Database
        # ApplicationModel.database.connect()
        # ApplicationModel.database.create_tables([Domain, Url, FileQueue], safe=True)

        super().__init__()


    def parse(self, response):
        # Return if Url has already been processed.
        # import pdb; pdb.set_trace()

        # The order of the following condition is required, first we check if domain_has_hit the limit
        # after that url_visited_before has to be checked.
        if has_hit_the_10k_limit(response) or url_visited_before(response):
            return

        # Sleep before proceeding further.
        # time.sleep(1)
        timestamp = int(time.time())

        create_dirs_for(current_domain(response))

        title = "_".join(response.css("title::text").getall()).replace("\n", "").strip() + f"-{timestamp}"

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

            # Check if we have reahed the limit for the current domain, we don't want to waste time by filling the queueu with links that we are going to skip.
            if fully_qualified_url and not has_hit_the_10k_limit(response):
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

    # json_body["text"] = ; json_body already has text attribute populated by trafil.extract function.
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
    return Url.select().where(Url.uri==response.url).count() > 0

def has_hit_the_10k_limit(response):
    domains = Domain.select().where(Domain.name==current_domain(response))

    # Only 10000 pages should be scrapped from a specific domain.
    if domains.exists() and Url.select().where(Url.domain == domains.get()).count() > 10000:
        return True

    return False


def run_spider(urls):
    print(f"Starting spider with {len(urls)} URLs")
    process = CrawlerProcess(get_project_settings())
    process.crawl(KodeSpider, start_urls=urls)
    process.start()
    print(f"Spider finished with {len(urls)} URLs")

if __name__ == "__main__":
    import subprocess

    # Connect Database
    ApplicationModel.database.connect()
    ApplicationModel.database.create_tables([Domain, Url, FileQueue], safe=True)

    urls = None
    pwd = os.path.dirname(os.path.abspath(__file__))
    process_num = int(os.getenv("NO_OF_SUB_SCRAPY_PROCESSES") or '4')

    with open(os.path.join(pwd, "domains.json"), "r") as file:
        data = json.load(file)
        urls = data["start_urls"]

    chunk_size = math.ceil(len(urls) / process_num)
    forward_ptr = chunk_size
    processes = []

    os.makedirs(os.path.join(KodeConfig.get("shared_data_path"), "scrapy_spider_state_dir"), exist_ok=True)

    for i in range(process_num):
        start = i * chunk_size
        end = min(start + chunk_size, len(urls))
        chunk = urls[start:end]

        url_list = " ".join(chunk)

        if chunk:
            job_dir_url = os.path.join(KodeConfig.get("shared_data_path"), "scrapy_spider_state_dir", f"spider-{i}")
            command = f"scrapy runspider kode.py -s JOBDIR={job_dir_url} -a urls='{url_list}' "

            print(command)

            p = subprocess.Popen(command, shell=True)
            processes.append(p)

    for p in processes:
        p.wait()
