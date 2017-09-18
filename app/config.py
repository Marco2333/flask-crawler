import os

class Config(object):
    DATABASE = 'sqlite:////tmp/app.db'
    DEBUG = False
    SECRET_KEY = "z\xe5v\xf1'\xde\x99\xa3P|\xa8\xd25op\xdd\xe96\r\xd3\xb7o"

    SQLALCHEMY_DATABASE_URI = 'mysql://root:123@127.0.0.1/flask_twitter'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    THREAD_NUM = 3

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOAD_FOLDER = 'app/static/uploads'

    APP_INFO = [{
            'consumer_key':'bRJ4nxfQ1lQpc0b9OiGyznwTP',
            'consumer_secret':'duDNQlvxtYInexf8kBiSTUwAuaskty4iGd6HnPKfoWzLoSvJgc',
            'access_token_key':'716652054446379008-4wz9tWCPDUa61FglUqrhk58zmJmtnP2',
            'access_token_secret':'hNFCesJ2rADFcmIljjEmywxGcDc6HrV6ORGZqrqNDWLXF'
        }
    ]

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True