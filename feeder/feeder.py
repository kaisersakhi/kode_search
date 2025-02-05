import json
from models.models import ApplicationModel, FileQueue
import os
import time
import requests

backoff_stage = 0

VESPA_URL = "http://vespa:8080/document/v1/kode_app/kode_document/docid/"

# id:kode_app:kode_document::<id>



def read_data(file_record):
    file_path = os.path.join("/data", file_record.path)
    ## load the file
    file = open(file_path, "r")
    data = json.load(file)
    file.close()

    return data

def feed_to_vespa(file_record):
    data = read_data(file_record)

    request_data = {
        "fields":{
            "title": data["title"],
            "text": data["text"],
            "timestamp": data["timestamp"],
            "url": data["url"]
        }
    }

    response = requests.post(
        VESPA_URL + file_record.id,
        headers={"Content-Type": "application/json"}, data=json.dumps(request_data)
    )

    if response.status_code == 200:
        print(response.json())

def backoff():
    stages = {
        0: 2,
        1: 10,
        2: 30,
        3: 120
    }

    time.sleep(stages[backoff_stage])

    backoff_stage = (backoff_stage + 1) % 4

if __file__ == "__main__":
    ApplicationModel.database.connect()

    while True:
        files = FileQueue.select().where(FileQueue.read==False)
        
        if not files:
            backoff()

        for file_record in files:
            feed_to_vespa(file_record)

            # mark the file_record as read


# https://localhost:8080/document/v1/kode_app/kode_document/docid/1