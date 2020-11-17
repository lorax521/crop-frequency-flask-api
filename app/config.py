import os

basedir = os.path.abspath(os.path.dirname(__file__))


class DevConfig:
    CONFIG_NAME = "default"
    DEBUG = True


class ProdConfig:
    CONFIG_NAME = "default"
    DEBUG = False
    host = "0.0.0.0"


class DBConfig:
    DB_PATH = 'db'
    REQUEST_EPSG = 'EPSG:4326'
