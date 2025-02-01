from peewee import PostgresqlDatabase, Model, CharField, TextField, ForeignKeyField, DateTimeField, BooleanField
import datetime
from kode_config import KodeConfig

db = PostgresqlDatabase(KodeConfig.db_name, user=KodeConfig.db_user, password=KodeConfig.db_password, host=KodeConfig.db_url, port=KodeConfig.db_port)

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

