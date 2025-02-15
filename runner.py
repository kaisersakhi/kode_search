import requests
from sentence_transformers import SentenceTransformer
import sys
import json
import time

model = SentenceTransformer("all-MiniLM-L6-v2")
VESPA_URL = "http://localhost:8080/search/"

def make_request(req_data):
    start_time = time.time()

    response = requests.post(
        VESPA_URL,
        headers = {"Content-Type": "application/json"}, data=json.dumps(req_data)
    )

    end_time = time.time()

    vespa_search_time = end_time - start_time

    data = None

    if response.status_code == 200:
        # import pdb; pdb.set_trace()
        data = response.json()

    return data, vespa_search_time


def vector_search(query):
    global model
    yql = "select * from kode_app where ({targetHits:10}nearestNeighbor(text_embedding, query_tensor))"
    ranking_profile = "kode_app"
    query_tensor = model.encode(query).tolist()

    req_data = {
        "yql": yql,
        "ranking": ranking_profile,
        "ranking.features.query(query_tensor)": query_tensor
    }

    data, vespa_search_time = make_request(req_data)

    if data is not None:
        docs = data["root"]["children"]

        for doc in docs:
            print(doc["fields"]["url"])

        print(f"Took {vespa_search_time * 1000} milliseconds")

def text_search(query):
    pass

def hybrid_search(query):
    pass


def help_text():
    return """
        Kode Search\n

    # Usage:
        # python3 "<query>" <option>

    # Options:
        # There is only one option:
            # -vs -> Search in vector space
            # -ts -> Search in raw text
            # -hs -> hybrid search
    """

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 2:
        print(help_text())

        exit(1)

    query = args[0]
    option = args[1]

    if option == "-vs":
        print(vector_search(query))
    elif option == "-ts":
        print(text_search(query))
    elif option == "-hs":
       print(hybrid_search(query))
    else:
      print(help_text())

    print(option)
