import json
from models.models import ApplicationModel, FileQueue
import os
import time
import requests
# from sentence_transformers import SentenceTransformer

backoff_stage = 0
# model = SentenceTransformer("all-MiniLM-L6-v2")

VESPA_URL = "http://vespa:8080/document/v1/kode_app/kode_app/docid/"
# VESPA_URL = "http://localhost:8080/document/v1/kode_app/kode_app/docid/"

# id:kode_app:kode_document::<id>

def read_data(file_record):
    data = None

    try:
        file_path = os.path.join("/data", file_record.path)
        # file_path = os.path.join("/Users/kaisersakhi/icode/crawling/kode_search/data", file_record.path)
        ## load the file
        file = open(file_path, "r")
        data = json.load(file)
        file.close()
    except Exception as e:
        print("Error occured while read file: ", e)

    return data

def feed_to_vespa(file_record):
    global model

    data = read_data(file_record)

    if data is None:
        return

    # import pdb; pdb.set_trace()
    # embedding = model.encode(data["text"]).tolist()

    request_data = {
        "fields":{
            "title": data["title"],
            "text": data["text"],
            "timestamp": data["timestamp"],
            "url": data["url"],
            # "text_embedding": [embedding]
            # "text_embedding": dumb_data
        }
    }

    response = requests.post(
        VESPA_URL + str(file_record.id),
        headers = {"Content-Type": "application/json"}, data=json.dumps(request_data)
    )

    if response.status_code == 200:
        print("Sucessfully fed data to vespa")
    else:
        print("Failed to feed data to vespa")

    print(response.json())

def backoff():
    global backoff_stage

    # Time range in minutes.
    stages = {
        0: 2,
        1: 10,
        2: 30,
        3: 120
    }

    print("Backingoff for ", stages[backoff_stage], " minutes...")

    time.sleep(stages[backoff_stage] * 60)

    backoff_stage = (backoff_stage + 1) % 4

if __name__ == "__main__":
    ApplicationModel.database.connect()

    while True:
        files = FileQueue.select().where(FileQueue.read==False)

        if not files:
            backoff()
        else:
            backoff_stage = 0

        for file_record in files:
            feed_to_vespa(file_record)

            # mark the file_record as read
            file_record.read = True
            file_record.save()


# https://localhost:8080/document/v1/kode_app/kode_document/docid/1



# curl -X POST -F "file=@/Users/kaisersakhi/icode/crawling/kode_search/vespa/application.zip" http://localhost:19071/application/v2/tenant/default/session
# curl -X POST -F "file=@/Users/kaisersakhi/icode/crawling/kode_search/data/kotlinlang.org/json_files/-1739076047.json" http://localhost:8080/document/v1/kode_app/kode_app/docid


# /Users/kaisersakhi/icode/crawling/kode_search/data/kotlinlang.org/json_files/-1739076047.json

# curl -X POST -H "Content-Type: -1739076047.json" -d @yourfile.json http://localhost:8080/document/v1/kode_app/kode_app/docid


# curl -X POST -H "Content-Type:application/json" --data '
#   {
#       "fields": {
#           "artist": "Coldplay",
#           "album": "A Head Full of Dreams",
#           "year": 2015
#       }
#   }' \
#   http://localhost:8080/document/v1/mynamespace/music/docid/a-head-full-of-dreams
# PUT


# vespa feed mind/vespa.json --target http://localhost:8080

# docker exec vespa bash -c '/opt/vespa/bin/vespa-deploy prepare /app/package && /opt/vespa/bin/vespa-deploy activate'


# curl -X GET "http://localhost:8080/search/?yql=SELECT * FROM kode_app * WHERE userQuery()" -d 'query=c++'
# curl -s "http://localhost:8080/search/?yql=select+*+from+kode_app+*+where+userQuery()" -d 'query=c'
