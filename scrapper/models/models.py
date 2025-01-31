from peewee import PostgresqlDatabase, Model, CharField, TextField, ForeignKeyField, DateTimeField
import datetime
from kode_config import KodeConfig

db = PostgresqlDatabase("kode_db", user="kaisersakhi", password="kaisersakhi", host="localhost", port=5433)

class ApplicationModel(Model):
    database = db
    class Meta:
        database = db

class Domain(ApplicationModel):
    name = CharField()

class Url(ApplicationModel):
    id = CharField(primary_key=True)
    title = CharField()
    body = TextField()
    html_file_path = CharField()
    domain = ForeignKeyField(Domain, backref='urls')
    downloaded_at = DateTimeField(default=datetime.datetime.now)

class FileQueue(ApplicationModel):
    url = ForeignKeyField(Url, backref='files_in_queue')
    path = CharField()

