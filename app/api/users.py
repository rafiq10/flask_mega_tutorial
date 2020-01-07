from flask import jsonify, request, url_for
from app import logging
from app.api import bp
from app.models import User, PaginateAPIMixin, get_all_users, create_user as cu
from app.api.errors import bad_request

@bp.route('/users/<id>',methods=['GET'])
def get_user(id):
  return jsonify(User(id).to_dict())

@bp.route('/users',methods=['GET'])
def get_users():
  # page = request.args.get('page',1,type=int)
  # per_page = min(request.args.get('per_page',10,type=int),100)
  # all_users = get_all_users()
  # data = jsonify( User.to_collection_dict(all_users,page,per_page,'api.get_users'))
  data = jsonify(get_all_users())
  return data

@bp.route('/users/<id>/following', methods=['GET'])
def get_followers(id):
  my_user = User(id)
  data = jsonify(my_user.get_am_followed_by_without_me())
  return data

@bp.route('/users/<id>/followed', methods=['GET'])
def get_followed(id):
  my_user = User(id)
  data = jsonify(my_user.get_am_following_without_me())
  return data

@bp.route('/users',methods=['POST'])
def create_user():
  
  TIF = request.form.get('TIF')
  full_name = request.form.get('full_name')
  country = request.form.get('country')
  department = request.form.get('department')
  pwd = request.form.get('pwd')
  about_me = request.form.get('about_me')

  if not  TIF or not country or not full_name or not pwd:
    return bad_request('must include TF, país, nombre y apellido y la contraseña')

  u = User(TIF)
  if u.TIF != "":
    logging.warn('User: ' + u.TIF)
    return bad_request('Please use differnt TIF')

  data = {'TIF': TIF, 'full_name': full_name, 'country': country, 'department': department, 'pwd': pwd, 'about_me': about_me}
  logging.warn('POST data: ' + str(data))
  cu(data)
  response = jsonify(User(TIF).to_dict())
  response.status_code = 201
  response.headers['Location']=url_for('api.get_user',id=TIF)
  return response

@bp.route('/users/<int:id>',methods=['PUT'])
def update_users(id):
  pass