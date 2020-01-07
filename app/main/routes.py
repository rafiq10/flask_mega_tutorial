import logging
from flask import request,render_template, flash, redirect, url_for, session, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from werkzeug.urls import url_parse
from app import login as my_login
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post, load_user, get_all_posts
from app.db import get_json_by_sql
from app.pagination import Pagination
from config import Config


@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
  form = PostForm()

  if form.validate_on_submit():
    Post(body = form.post.data, author = current_user)
    flash(_('Your post is now live!'))
    return redirect(url_for('main.index'))

  page = request.args.get('page', 1, type=int)
  my_posts = current_user.get_followed_posts()
  my_pagination = Pagination(my_posts)
  page_posts = my_pagination.get_page(page)
  next_url = url_for('main.index', page=my_pagination.next_num()) \
              if my_pagination.has_next() else None
  prev_url = url_for('main.index', page=my_pagination.prev_num()) \
              if my_pagination.has_prev() else None

  return render_template('index.html',title='Home', form=form,
                        posts=page_posts, 
                        next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
  my_user = User(username)
  my_posts = []
  posts = get_json_by_sql("select postText as body from RRHH_blogPosts as p where TF = '" + username + "'")
  for post in posts:
    my_posts.append({'author': my_user, 'body': post.body})

  page = request.args.get('page', 1, type=int)
  my_posts = my_user.followed_posts_bodies()
  my_pagination = Pagination(my_posts)
  page_posts = my_pagination.get_page(page)

  next_url = url_for('main.user', username = my_user.TIF ,page=my_pagination.next_num()) \
              if my_pagination.has_next() else None
  prev_url = url_for('main.user', username = my_user.TIF, page=my_pagination.prev_num()) \
              if my_pagination.has_prev() else None

  
  return render_template('user.html', user=my_user, posts = page_posts,
                        next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  
  form = EditProfileForm()
  user = User(current_user.get_id())

  if form.validate_on_submit():
    user = User(current_user.get_id())
    user.fullName = form.username.data
    user.about_me = form.about_me.data
    user.certPwd = form.pwd.data
    user.update_user()
  elif request.method == 'GET':
    form.username.data = current_user.fullName
    form.about_me.data = current_user.about_me
    form.pwd.data = ''
  return render_template('edit_profile.html', title = 'Edit Profile', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
  user = User(my_tif=username)
  if user is None:
    flash(_('User %(username)s not found.', username=username))
    return redirect(url_for('main.index'))
  if user == current_user:
    flash(_('You cannot follow yourself!'))
    return redirect(url_for('main.user', username = username))
  current_user.follow(user)
  flash(_('You are following %(username)s!', username=username))
  return redirect(url_for('main.user', username = username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
  user = User(my_tif=username)
  if user is None:
    flash(_('User %(username)s not found.', username=username))
    return redirect(url_for('main.index'))
  if user == current_user:
    flash(_('You cannot unfollow yourself!'))
    return redirect(url_for('main.user',username = username))
  current_user.unfollow(user)
  flash(_('You are not following %(TF)s', TF=username))
  return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required
def explore():
  page = request.args.get('page', 1, type=int)
  my_posts = get_all_posts()
  my_pagination = Pagination(my_posts)
  page_posts = my_pagination.get_page(page)

  next_url = url_for('main.explore', page=my_pagination.next_num()) \
              if my_pagination.has_next() else None
  prev_url = url_for('main.explore', page=my_pagination.prev_num()) \
              if my_pagination.has_prev() else None

  return render_template('index.html', title = 'Explore', posts = page_posts,
                        next_url=next_url, prev_url=prev_url)

@bp.before_request
def before_request():
  if current_user.is_authenticated:
    current_user.save_visit(request.url)
  g.locale = str(get_locale())