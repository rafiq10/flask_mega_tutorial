import logging
import datetime
import app
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import String, Date, Boolean
from hashlib import md5
from app.db import get_json_by_sql, save_to_db
from app.pagination import Pagination
from config import Config
from app import login


class PaginateAPIMixin(object):
  @staticmethod
  def to_collection_dict(items, page, per_page, endpoint, **kwargs):
    p = Pagination(items)
    resources = p.get_page(page)
    
    data = {
      'items': [item.to_dict() for item in resources.items],
      '_meta': {
        'page': page,
        'per_page': per_page,
        'total_pages': p.num_pages,
        'total_items': items.count
      },
      '_links': {
        'self': url_for(endpoint=endpoint, page=page, per_page=per_page, **kwargs),
        'next': url_for(endpoint=endpoint, page=page+1, per_page=per_page, **kwargs),
        'prev': url_for(endpoint=endpoint, page=page-1, per_page=per_page, **kwargs)
      }
    }
    return data

class User(PaginateAPIMixin):

  def __init__(self, my_tif):
    my_sql = "select TIF, country, department,fullName,activeUntil, cast(DECRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), certPwd,N'" + Config.DB_DECRYPT_PWD + "') as varchar(max)) as pwd, last_seen, about_me from tblUsers where TIF='" + my_tif + "'"
    self.my_resp = get_json_by_sql(my_sql)
    self.following = get_json_by_sql("select followedTF from RRHH_followers where followerTF = '" + str(my_tif) + "'")
    self.followed = get_json_by_sql("select followerTF from RRHH_followers where followedTF = '" + str(my_tif) + "'")

    if not (self.my_resp):
      self.TIF = ""
      self.country = ""
      self.department = ""
      self.fullName = ""
      self.activeUntil = "1900-01-01"
      self.certPwd = ""
      self.email = ""
      self.last_seen = "1900-01-01"
      self.about_me = ""
      self.is_actived = False
      self.is_anonym = False
    else:
      self.TIF = self.my_resp[0][0]
      self.country = self.my_resp[0][1]
      self.department = self.my_resp[0][2]
      self.fullName = self.my_resp[0][3]
      self.activeUntil = str(self.my_resp[0][4])

      self.last_seen = self.my_resp[0][6]
      self.about_me = self.my_resp[0][7]

      if self.my_resp[0][5]:
        self.certPwd = generate_password_hash(self.my_resp[0][5])
      else:
        self.certPwd = generate_password_hash("")

      self.email = self.fullName + "@telefonica.com"
      if self.activeUntil is not None:
        self.is_actived = False
        self.is_anonym = False
      else:
        self.is_actived = True
        self.is_anonym = True
      self.is_authted = False

    self.am_following = []
    for r in self.following:
      self.am_following.append(str(r[0]))

    self.am_followed_by = []
    for r in self.followed:
      self.am_followed_by.append(str(r[0]))

    self.my_followed_postIds = []
    self.my_followed_posts = []
    self.my_followed_postDates = []
    self.my_followed_postsUsers = []
    self.update_followed_posts()
  
  def is_authenticated(self):
    """Return True if the user is authenticated."""
    return bool(self.is_authted)

  def is_active(self):
    """Return True if the user is active."""
    return self.is_actived

  def is_anonymous(self):
    """Return True if the user is anonymous."""
    return self.is_anonym

  def get_id(self):
    return self.TIF
  
  def check_password(self, pwd):
    if self.my_resp:
      return check_password_hash(self.certPwd,pwd)

  def get_country(self):
    if self.my_resp:
      return self.country

  def get_department(self):
    if self.my_resp:
      return self.department

  def get_last_seen(self):
    return datetime.datetime.strptime(self.last_seen, '%Y-%m-%d %H:%M:%S') 

  def get_about_me(self):
    return self.about_me

  def set_last_login(self):
    the_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    the_time_str = str(the_time)[:str(the_time).find(".")]
    save_to_db("update tblUsers set last_seen = '" + the_time_str + "' where TIF = '" + self.TIF + "'" )
    save_to_db("insert into tblWebStats (TF,login_time, url_visit_time, url_visited) values('" + self.TIF + "','" + the_time_str + "', '" + the_time_str + "', '" + Config.ENV_BASE_URL + "login')")

  def save_visit(self, my_url):
    the_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    the_time_str = str(the_time)[:str(the_time).find(".")]
    save_to_db("insert into tblWebStats (TF, url_visit_time, url_visited) values('" + self.TIF + "','" + the_time_str + "', '" + my_url + "')")

  def set_password(self, new_wpd):
    self.certPwd = generate_password_hash(new_wpd)

    save_to_db("update tblUsers set  certPwd = ENCRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), '" + new_wpd + "' ) where TIF = '" + self.TIF + "'")

  def update_user(self):
    save_to_db("update tblUsers set fullName = '" + self.fullName + "', certPwd = ENCRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), '" + self.certPwd + "' ), about_me = '" + self.about_me + "' where TIF = '" + self.TIF + "'")

  def avatar(self, size):
    digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
      digest, size
    )

  def is_following(self, my_TIF):
    return (my_TIF in self.am_following)

  def get_am_followed_by(self):
    return(self.am_followed_by)

  def get_am_followed_by_without_me(self):
    new_list = []

    for i in self.am_followed_by:
      if i != self.TIF:
        new_list.append(i)
    return new_list

  def get_am_following(self):
    return(self.am_following)

  def get_am_following_without_me(self):
    new_list = []

    for i in self.am_following:
      if i != self.TIF:
        new_list.append(i)
    return new_list


  def follow(self, user):
    userTF = user.TIF
    if not self.is_following(userTF):
      user.am_followed_by.append(self.TIF)
      save_to_db("insert into RRHH_followers (followerTF, followedTF) values('" + str(self.TIF) + "','" + userTF + "')")
      self.am_following.append(userTF) 
      self.update_followed_posts()

  def unfollow(self, user):
    userTF = user.TIF
    if self.is_following(userTF):
      user.am_followed_by.remove(self.TIF)

      save_to_db("delete from RRHH_followers where followedTF = '" + userTF + "'")
      self.am_following.remove(userTF)
      self.update_followed_posts()

  def get_followed_posts(self):
    my_posts = []
    for i in range(len(self.my_followed_posts)):
      my_posts.append({
        'author': User(self.my_followed_postsUsers[i]), 
        'body': self.my_followed_posts[i]['body'], 
        'post_date': datetime.datetime.strptime(self.my_followed_postDates[i], '%Y-%m-%d %H:%M:%S') 
      })
    return my_posts

  def followed_posts_users(self):
    return self.my_followed_postsUsers

  def followed_posts_bodies(self):
    return self.my_followed_posts
  
  def followed_postsDates(self):
      return self.my_followed_postDates

  def add_post(self,post_text):
    save_to_db("insert into RRHH_blogPosts (TF, postText, postDate) values ('" + self.TIF +  "','" + post_text + "', getdate())")
    self.update_followed_posts()

  def update_followed_posts(self):
    my_sql = """select distinct * from (select p.*, u.fullName from RRHH_blogPosts as p
      left join tblUsers as u on p.TF = u.TIF
      where exists (select f.followedTF as TF from RRHH_followers as f where f.followerTF = '""" + self.TIF + """' and f.followedTF = p.TF)
      union all
      (select p.*, u.fullName from RRHH_blogPosts as p  
      left join tblUsers as u on p.TF = u.TIF
      where p.TF = '""" + self.TIF + """'
      )) as a
      order by postId
      """

    self.self_followed_posts = get_json_by_sql(my_sql)
    self.my_followed_postIds = []
    self.my_followed_posts = []
    self.my_followed_postDates = []
    self.my_followed_postsUsers = []
    
    for r in self.self_followed_posts:
      self.my_followed_postIds.append(str(r[0]))
      self.my_followed_postsUsers.append(str(r[1]))
      self.my_followed_posts.append({'author': {
                                        'TIF': str(r[1]), 
                                        'fullName': str(r[4]), 
                                        'avatar': self.avatar
                                        }, 
                                      'body': str(r[2]),
                                      'post_date': datetime.datetime.strptime(str(r[3])[:str(r[3]).find(".")],'%Y-%m-%d %H:%M:%S')
                                    })
      self.my_followed_postDates.append(str(r[3])[:str(r[3]).find(".")])
  
  def to_dict(self):
    data={
      # 'id': self.TIF,
      'TF': self.TIF,
      'full name': self.fullName,
      'last_seen': self.last_seen,
      'about_me': self.about_me,
      'follower_count': len(self.am_following),
      'followed_count': len(self.am_followed_by),
      'followed_by': self.followed,
      'following': self.following
    }
    return data

  def from_dict(self, data, new_user=False):
    for field in ['username', 'about_me']:
      if field in data:
        setattr(self, field, data[field])
    
class Post():
  """ kwarg(1) = 'author', kwarg(2) = 'body """
  def __init__(self, **kwargs):
    if self.is_key_in_keys('id', kwargs):
      my_id = kwargs['id']
      my_sql = "select postId, TF, postText, postDate from RRHH_blogPosts where postId='" + my_id + "'"
      self.my_resp = get_json_by_sql(my_sql)
      self.post_id = self.my_resp[0][0]
      self.author = User(my_tif=self.my_resp[0][1])
      self.body = self.my_resp[0][2]
      self.post_date = datetime.datetime.strptime(self.my_resp[0][3], '%Y-%m-%d %H:%M:%S') 
      self.lang = app.get_locale()

    elif (self.is_key_in_keys('author', kwargs) and self.is_key_in_keys('body', kwargs)) :
      the_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
      the_time_str = str(the_time)[:str(the_time).find(".")]
      self.author = kwargs['author']
      self.body = kwargs['body']
      self.post_date = the_time
      self.lang = app.get_locale()
      
      save_to_db("insert into RRHH_blogPosts (TF, postText, postDate, postLanguage) values('" + self.author.TIF + "','" + self.body + "','" + the_time_str + "','" + self.lang + "')")
    else:
      pass

  def is_key_in_keys(self, my_key, keys=[]):
    for key in keys:
      if key == my_key:
        return True
    return False


@login.user_loader
def load_user(id):
  my_user = User(id)
  return my_user


def get_all_posts():
  my_sql = "select * from RRHH_blogPosts order by postDate desc"
  my_resp = get_json_by_sql(my_sql)
  all_posts = []
  for r in my_resp:
    all_posts.append({'author': User(r.TF), 'body': r.postText, 'post_date': datetime.datetime.strptime(r.postDate[:str(r.postDate).find(".")], '%Y-%m-%d %H:%M:%S') })
  return all_posts


    

def get_all_users():
  my_sql = "select * from tblUsers order by TIF desc"
  my_resp = get_json_by_sql(my_sql)
  all_users = []
  for r in my_resp:
    all_users.append({'TIF': r.TIF, 'country': r.country, 'department': r.department, 'last_seen': r.last_seen, 'about_me': r.about_me })
  return all_users

def create_user(data):
  
  TIF = data['TIF']
  country= data['country']
  department = data['department']
  fullName = data['full_name']
  certPwd = data['pwd']
  about_me = data['about_me']

  my_sql = "insert into tblUsers (country, TIF, department, fullName, certPwd, about_me, last_seen) values ('" + \
           country + "','" + TIF + "', '" + department + "','" + fullName + "', ENCRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), '" + certPwd + "'), '" + about_me + "', '1900-01-01')"
  
  save_to_db(my_sql)

def update_user(data, TF):
  fields = ""
  for k in data:
    if not data[k] == "":
      if k == 'certPwd':
        fields = fields + str(k) + " = ENCRYPTBYASYMKEY(ASYMKEY_ID('ClaveAsym'), '" + str(data[k]) + "'),"
      else:
        fields = fields + str(k) + " = '" + str(data[k]) + "',"

  fields = fields[:len(fields)-1]
  

  my_sql = "update tblUsers set " + fields + " where TIF = '" + TF + "'"
  logging.warn(my_sql)
  save_to_db(my_sql)