import logging
import json
import datetime
from collections import namedtuple
from app import my_session, engine

def _json_object_hook(d):
  return namedtuple('X', d.keys())(*d.values())

def my_converter(o):
  if isinstance(o, datetime.datetime):
    return o.__str__()

def json2obj(data):
  a = json.dumps(data, default=my_converter)
  return json.loads(a, object_hook=_json_object_hook)
  
def get_json_by_sql(my_sql):
  d, a = {}, []
                                              
  sess = my_session
  try:
    result = sess.execute(my_sql,{})
  except:
    sess.rollback()

  for rowproxy in result:
    for column, value in rowproxy.items():
      d = {**d, **{column: value}}
    a.append(d)
                                          
  return json2obj(a) 

def save_to_db(my_sql):
  # logging.warning('my_sql in save_to_db: ' + my_sql)
  con = engine.connect()
  # my_sql = "SET NOCOUNT ON " + my_sql
  con.execute(my_sql)
  logging.warning('my_sql in save_to_db: ' + my_sql)
  con.close()