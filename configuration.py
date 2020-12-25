from hashlib import sha3_512


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgres://zyndwtjwqtrmve' \
                              ':25d497da910d665f65a4ac982f6ee0138b126e42fb6150d20eb36c8b95a8b150@ec2-18-203-7-163.eu' \
                              '-west-1.compute.amazonaws.com:5432/dd2sglh2cjcflv'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = sha3_512('xenofium'.encode()).hexdigest()


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
