from flask import jsonify, request, url_for, g, abort
from app import logging
from app.api import bp
from app.models import User, PaginateAPIMixin, get_all_users, create_user as cu, update_user as uu
from app.api.errors import bad_request
from app.api.auth import token_auth

@bp.route('/users/<id>',methods=['GET'])
@token_auth.login_required
def get_user(id):
  return jsonify(User(id).to_dict())

@bp.route('/users',methods=['GET'])
@token_auth.login_required
def get_users():
  data = jsonify(get_all_users())
  return data

@bp.route('/users/<id>/following', methods=['GET'])
@token_auth.login_required
def get_followers(id):
  my_user = User(id)
  data = jsonify(my_user.get_am_followed_by_without_me())
  return data

@bp.route('/users/<id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
  my_user = User(id)
  data = jsonify(my_user.get_am_following_without_me())
  return data

@bp.route('/users',methods=['POST'])
@token_auth.login_required
def create_user():
  
  TIF = request.form.get('TIF')
  full_name = request.form.get('full_name')
  country = request.form.get('country')
  pwd = request.form.get('pwd')

  if not  TIF or not country or not full_name or not pwd:
    return bad_request('must include TF, país, nombre y apellido y la contraseña')

  u = User(TIF)
  if u.TIF != "":
    return bad_request('Please use differnt TIF')

  data = dict(request.form)
  if not 'department' in data:
    data['department'] = ""
  if not 'about_me' in data:
    data['about_me'] = ""

  cu(data)
  response = jsonify(User(TIF).to_dict())
  response.status_code = 201
  response.headers['Location']=url_for('api.get_user',id=TIF)
  return response

@bp.route('/users/<id>',methods=['PUT'])
@token_auth.login_required
def update_users(id):
  if g.current_user.TIF != id:
    abort(403)
  u = User(str(id))
  logging.warn('u.TF: ' + u.TIF)
  if u.TIF == "":
    return bad_request('El TF ' + id + ' no encontrado')

  data = dict(request.form)
  uu(data, id)
  response = jsonify(User(id).to_dict())
  return response