from peewee import PostgresqlDatabase, Model, CharField, TextField, ForeignKeyField, DateTimeField, BooleanField
import datetime
from kode_config import KodeConfig
import os

db = PostgresqlDatabase(
        KodeConfig.get("db_name"),
        user=KodeConfig.get("db_user"),
        password=KodeConfig.get("db_password"),
        host=KodeConfig.get("db_url"),
        port=KodeConfig.get("db_port")
    )

class ApplicationModel(Model):
    database = db
    class Meta:
        database = db

class Domain(ApplicationModel):
    name = CharField(index=True, unique=True)

class Url(ApplicationModel):
    uri = CharField(index=True, unique=True)
    title = CharField(index=True)
    html_file_path = CharField()
    domain = ForeignKeyField(Domain, backref='urls')
    downloaded_at = DateTimeField(default=datetime.datetime.now)

class FileQueue(ApplicationModel):
    url = ForeignKeyField(Url, backref='files_in_queue')
    path = CharField()
    read = BooleanField(default=False)

