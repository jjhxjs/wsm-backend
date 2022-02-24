from .. import db
from sqlalchemy import event, or_
from sqlalchemy.orm.query import Query

class BaseModel(db.Model):
    # 支持model的继承，目的是为了抽离出公共逻辑
    __abstract__ = True

    def __str__(self):
        columns = {c.name: getattr(self, c.name)
                   for c in self.__table__.columns}
        return str(columns)

    # 把SQLAlchemy查询对象转换成字典
    def to_dict(self):
        columns = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return columns

    __repr__ = __str__

from .book import *