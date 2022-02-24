from app import db
from . import BaseModel
from sqlalchemy.dialects.mysql import LONGTEXT,TINYTEXT


class Content_Indices(BaseModel):
    __tablename__ = 'content_indices'
    __table_args__ = {"useexisting": True}

    term = db.Column(db.String(255), primary_key=True)
    book_id = db.Column(db.Integer, primary_key=True)
    indices = db.Column(LONGTEXT)
    tf = db.Column(db.BigInteger)
    tf_wt = db.Column(db.Float)
