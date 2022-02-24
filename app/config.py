
"""
应用内公共配置
"""

import os
from flask_log_request_id import RequestIDLogFilter
import redis

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASEDIR = basedir
    # 此处定义全局变量
    SECRET_KEY = os.environ.get('SECRET_KEY') or '!@#$%^&*12345678'  # 设置密钥，可能会用在某些涉及到加解密的功能中
    SQLALCHEMY_TRACK_MODIFICATIONS = True                            # 该项不设置为True的话可能会导致数据库报错

    SESSION_TYPE = 'redis'
    REDIS_ENDPOINT = '127.0.0.1'
    SESSION_REDIS = redis.from_url('redis://%s:6379' % REDIS_ENDPOINT)
    # 分页
    FLASK_PER_PAGE = 6
    LOG_PATH = os.path.join(basedir, 'wsm.log')


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    # 定时任务 配置
    SCHEDULER_API_ENABLED = True

    LOG_CONFIG = {
        'version': 1,
        'formatters': {'default': {
            # ref:https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': '[%(asctime)s--%(request_id)s] %(levelname)s[%(filename)s:%(funcName)s:%(lineno)d]: %(message)s',
        }},
        'filters': {
            'request_id_filter': {
                '()': RequestIDLogFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                # 'stream': 'ext://flask.logging.wsgi_errors_stream',
                'stream': 'ext://sys.stdout',
                'formatter': 'default',
                'filters': ['request_id_filter'],
            },
            'logfile': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filters': ['request_id_filter'],
                'filename': Config.LOG_PATH,
                'mode': 'a',
                'maxBytes': 300 * 1024 * 1024,
                'backupCount': 5,
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'logfile']
        }
    }

    # 云上平台数据库的URL
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DEV_DATABASE_URL') or
                               'mysql://yx:123456@202.120.38.212:3306/wsm?charset=utf8mb4')
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS') or 'redis://127.0.0.1:6379')

    # 连接测试环境数据库的URL
    # SQLALCHEMY_DATABASE_URI = (os.environ.get('DEV_DATABASE_URL') or
    #                            'mysql://test_user:test_passwd1024@gotms.cn:3306/zxt?charset=utf8mb4')


class ProductionConfig(Config):
    def __init__(self):
        pass

    DEBUG = False

    # 定时任务 配置
    SCHEDULER_API_ENABLED = True

    SQLALCHEMY_DATABASE_URI = 'mysql://yx:123456@202.120.38.212:3306/wsm?charset=utf8mb4'

    LOG_CONFIG = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s--%(request_id)s] %(levelname)s[%(filename)s:%(funcName)s:%(lineno)d]: %(message)s',
        }},
        'filters': {
            'request_id_filter': {
                '()': RequestIDLogFilter,
            }
        },
        'handlers': {
            'logfile': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'default',
                'filters': ['request_id_filter'],
                'filename': Config.LOG_PATH,
                'mode': 'a',
                'maxBytes': 300 * 1024 * 1024,
                'backupCount': 5,
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['logfile', ]
        }
    }
    PRIVACY_PHONE_SERVICE = {
        "token": '5e539e695fd9a70007af7051bce88ec8',
        "user_id": '948',
        "appkey": '948',
        "expiration": 120,
    }
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS') or 'redis://127.0.0.1:6379')


class StagingConfig(Config):
    DEBUG = False

    TEMPLATES_AUTO_RELOAD = True
    # 定时任务 配置
    SCHEDULER_API_ENABLED = True

    LOG_CONFIG = {
        'version': 1,
        'formatters': {'default': {
            # ref:https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': '[%(asctime)s--%(request_id)s] %(levelname)s[%(filename)s:%(funcName)s:%(lineno)d]: %(message)s',
        }},
        'filters': {
            'request_id_filter': {
                '()': RequestIDLogFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default',
                'filters': ['request_id_filter'],
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }

    # 云上平台数据库的URL
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DEV_DATABASE_URL') or
                               'mysql://yx:123456@localhost:3306/wsm?charset=utf8mb4')
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('SESSION_REDIS') or 'redis://127.0.0.1:6379')


config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}


def get_config():
    from app.config import config
    return config[os.getenv('FLASK_ENV')]
    # return config[os.getenv('APP_CONFIG')]
