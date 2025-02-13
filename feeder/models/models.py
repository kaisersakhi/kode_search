from peewee import PostgresqlDatabase, Model, CharField, ForeignKeyField, DateTimeField, BooleanField
import datetime
import os

db = PostgresqlDatabase(
        os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_URL"),
        port=os.getenv("DB_PORT")
    )

# db = PostgresqlDatabase(
#         "kode_app",
#         user="kaisersakhi",
#         password="kaisersakhi",
#         host="localhost",
#         port=5433
#     )


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
