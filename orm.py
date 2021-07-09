import os

from dotenv import load_dotenv
from peewee import *

load_dotenv()
db = MySQLDatabase('policy-research',
                   user=os.getenv('DATABASE_USER'),
                   password=os.getenv('DATABASE_PASSWORD'),
                   host=os.getenv('DATABASE_HOST'),
                   port=int(os.getenv('DATABASE_PORT')),
                   charset='utf8mb4')


class BaseModel(Model):
    class Meta:
        database = db


class Article(BaseModel):
    index_code = CharField()
    document_code = CharField()
    categories = CharField()
    title = CharField()
    author = CharField()
    content = TextField()
    url = CharField(unique=True)
    created_at = DateField()
    published_at = DateField()

    class Meta:
        table_name = 'articles'


class News(BaseModel):
    title = CharField()
    content = TextField()
    date = DateField()

    class Meta:
        table_name = 'news'
