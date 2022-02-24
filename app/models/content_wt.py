from app import db
from . import BaseModel
from sqlalchemy.dialects.mysql import LONGTEXT,TINYTEXT


class  Content_Weight(BaseModel):
    __tablename__ = 'content_wt'
    __table_args__ = {"useexisting": True}

    term = db.Column(db.String(255), primary_key=True)
    df = db.Column(db.BigInteger)
    idf = db.Column(db.Float)
