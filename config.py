import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_DECRYPT_PWD = os.environ.get('DB_DECRYPT_PWD')

    ENV_BASE_URL = "http://localhost:5000/"

    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_LTS = 1
    MAIL_USERNAME = "rafiq10@gmail.com"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['rafal.bil@telefonica.com']

    POSTS_PER_PAGE = 5

    LANGUAGES = ['en','es''pl']