
PG_HOST = 'localhost'
PG_PASSWORD = 'pass'
PG_USER = 'myuser'
PG_DATABASE = 'db'



class Configuration(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DATABASE}'
    SQLALCHEMY_POOL_SIZE = 1

    SECRET_KEY = 'someth3489rh6&r65r^R#2$%GkBHJKN98 secret'

    SECURITY_PASSWORD_SALT = 'salt'
    SECURITY_PASSWORD_HASH = 'sha512_crypt'