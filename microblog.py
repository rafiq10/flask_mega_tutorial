from app import create_app, db, cli
# from app.email import send_mail
import tests
from app.models import User
from app import login
from flask_login import current_user

app = create_app()
cli.register(app=app)

@app.shell_context_processor
def make_shell_processor():
  return {'db': db.my_session, 'User': User,
          'login': login, 'current_user': current_user, 'tests': tests
          # , 'send_mail': send_mail
          }