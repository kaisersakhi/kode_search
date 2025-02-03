import json
from models.models import ApplicationModel, FileQueue

if __file__ == "__main__":
    ApplicationModel.database.connect()


    while True:
        files = FileQueue.select().where(FileQueue.read==False)

        for file in files:
            file_path = file.path

            
def feed_to_vespa(data):
    pass