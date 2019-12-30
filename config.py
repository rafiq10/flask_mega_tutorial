import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://Rafal:Rfl2206@datacluster/TIS_FinanzasGlobal'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_DECRYPT_PWD = '0RAN1ger5@'

    ENV_BASE_URL = "http://localhost:5000/"

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_LTS = 1
    MAIL_USERNAME = "rafiq10@gmail.com"
    MAIL_PASSWORD = "KA9ka8o7"
    ADMINS = ['rafal.bil@telefonica.com']

    POSTS_PER_PAGE = 5

    LANGUAGES = ['en','es']