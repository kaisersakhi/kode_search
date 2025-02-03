# rm -rf ./data/*

# docker-compose up -d

if [ -f "scrapper/venv/bin/activate" ]; then
    source scrapper/venv/bin/activate
fi

scrapy runspider scrapper/kode.py -s JOBDIR=data/scrapy_spider_state -s CONCURRENT_REQUESTS=32 -s LOG_LEVEL=INFO
# python3 scrapper/kode.py