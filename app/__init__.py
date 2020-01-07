from flask import Flask, request, current_app
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

import config
from config import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import (scoped_session, sessionmaker, Session)
from flask_login import LoginManager

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
my_session = Session(bind=engine)
db_session = scoped_session(sessionmaker(automatic = False,
                                          autoFlash=False,
                                          bind=engine
  ))

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(Config)

  login.init_app(app=app)
  mail.init_app(app=app)
  bootstrap.init_app(app=app)
  moment.init_app(app=app)
  babel.init_app(app=app)

  from app import models

  from app.errors import bp as errors_bp
  app.register_blueprint(errors_bp)

  from app.auth import bp as auth_bp
  app.register_blueprint(auth_bp, url_prefix='/auth')

  from app.main import bp as main_bp
  app.register_blueprint(main_bp)

  from app.api import bp as api_bp
  app.register_blueprint(api_bp, url_prefix='/api')


  if not app.debug and not app.testing:
    # logging.warning('in mail')
    if not app.config['MAIL_SERVER']:
      auth = None
      # logging.warning('MAIL_USERNAME: ' + str(app.config['MAIL_USERNAME']))
      if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
        auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
      
      secure = None
      if app.config['MAIL_USE_LTS']:
        secure=()
      
      mail_handler = SMTPHandler(
        mailhost=(app.config['MAIL_SERVER'],app.config['MAIL_PORT']),
        fromaddr='no-reply@' + str(app.config['MAIL_SERVER']),
        toaddrs=app.config['ADMINS'], subject='Microblog Failure',
        credentials=auth, secure=secure
      )
      mail_handler.setLevel(logging.ERROR)
      app.logger.addHandler(mail_handler)
    
    if not os.path.exists('logs'):
      os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log',maxBytes=10240,backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
  return app


@babel.localeselector
def get_locale():
  return request.accept_languages.best_match(current_app.config['LANGUAGES']) # 

from app import models