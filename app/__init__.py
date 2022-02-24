from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config
from flask_log_request_id import RequestID, RequestIDLogFilter
import uuid
from flask_cache import Cache


class JSONEncoder(_JSONEncoder):
    """ 解决decimal类型无法序列化的问题 """

    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
            return float(o)

        super(JSONEncoder, self).default(o)


class Flask(_Flask):
    json_encoder = JSONEncoder


db = SQLAlchemy()


app = Flask(__name__)



""" 此函数由falsk工厂调用，启动app """
# ref: https://pypi.org/project/Flask-Log-Request-ID/
RequestID(app, request_id_generator=lambda: uuid.uuid4().hex[:15])

# 加载配置
app.config.from_object(get_config())
app.secret_key = '!@#$%^&*12345678'
print("Load config successfully!")
# 注册必要拓展

db.init_app(app)

# 注册缓存redis 机制

cache = Cache(
    app,
    config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': '127.0.0.1',
        'CACHE_REDIS_PORT': 6379
        # 'CACHE_REDIS_PASSWORD': '123456',
        # 'CACHE_REDIS_DB': 0
    }
)
cache.init_app(app)

from logging.config import dictConfig

dictConfig(app.config["LOG_CONFIG"])

from app.views import *
