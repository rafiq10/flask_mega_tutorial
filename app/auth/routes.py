from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User(form.username.data)
        if not user.check_password(form.password.data):
          flash(_('Invalid username or password'))
          return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        current_user.set_last_login()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
          next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))