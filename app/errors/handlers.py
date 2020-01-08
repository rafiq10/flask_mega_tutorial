from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

def wants_json_reposnse():
  return request.accept_mimetypes['application/json'] >= \
    request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
  if wants_json_reposnse():
    return api_error_response(404)
  return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
  db.my_session.rollback()
  if wants_json_reposnse():
    return api_error_response(500)
  return render_template('500.html'), 500