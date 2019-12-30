import logging
from flask import request
from math import ceil
from config import Config
from app.db import get_json_by_sql, save_to_db

class Pagination():
  """ pass the list of items to paginate 
      and it will return items corresponding to the page number and Config.POSTS_PER_PAGE """

  def __init__(self, elems):
    self.elems = elems
    self.posts_per_page = Config.POSTS_PER_PAGE
    self.current_page = request.args.get('page', 1, type=int)
    self.my_pages = []
    self.paginate()

  def get_page(self, num_page):
    logging.warning('num_page: ' + str(num_page))
    my_page = self.my_pages[num_page-1]
    the_page = my_page['page_elems']
    return the_page

  def next_num(self):
    if self.has_next():
      return self.current_page+1
    else:
      return None

  def prev_num(self):
    if self.has_prev():
      return self.current_page-1
    else:
      return None

  def has_next(self):
    return (len(self.my_pages)> self.current_page)
  
  def has_prev(self):
    return (self.current_page>1)

  def paginate(self):
    num_pages = ceil(len(self.elems) / self.posts_per_page)+1
    for num_page in range(1, num_pages):
      page_elems=[]
      my_x = ((num_page)*self.posts_per_page,len(self.elems))
      last_elem = min(my_x)
      for i in range((num_page-1)*self.posts_per_page, last_elem):
        page_elems.append(self.elems[i])
      self.my_pages.append({'num_page': num_page, 'page_elems': page_elems})
      
