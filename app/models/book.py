from app import db
from . import BaseModel
from sqlalchemy.dialects.mysql import LONGTEXT,MEDIUMTEXT


class Book(BaseModel):
    __tablename__ = 'book'
    __table_args__ = {"useexisting": True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    content = db.Column(LONGTEXT)
    year = db.Column(db.Integer)
    description = db.Column(MEDIUMTEXT)
    url_index = db.Column(db.String(255))
    url_epub = db.Column(db.String(255))
    url_txt = db.Column(db.String(255))
    language = db.Column(db.String(255))
