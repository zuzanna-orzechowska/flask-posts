import functools
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskpost.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        r = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif r.exists(f"username_to_id:{username}"):
            error = f"User {username} is already registered."

        if error is None:
            user_id = r.incr("next_user_id")
            is_admin = 1 if r.llen("user_ids") == 0 else 0

            r.hset(f"user:{user_id}", mapping={
                "username": username,
                "password": generate_password_hash(password),
                "is_admin": is_admin
            })
            r.rpush("user_ids", user_id)
            r.set(f"username_to_id:{username}", user_id)

            return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        r = get_db()
        error = None

        user_id = r.get(f"username_to_id:{username}")
        if not user_id:
            error = 'Incorrect username.'
        else:
            user = r.hgetall(f"user:{user_id}")
            stored_hash = None
        if b'password' in user:
            stored_hash = user[b'password'].decode()
        elif 'password' in user:
            stored_hash = user['password']

        if not stored_hash or not check_password_hash(stored_hash, password):
            error = 'Incorrect password.'


        if error is None:
            session.clear()
            session['user_id'] = user_id
            session['is_admin'] = bool(int(user['is_admin']))
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        r = get_db()
        user = r.hgetall(f"user:{user_id}")
        if not user:
            g.user = None
        else:
            g.user = {
                "id": user_id,
                "username": user['username'],
                "password": user['password'],
                "is_admin": int(user['is_admin'])
            }

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or not g.user['is_admin']:
            flash("Administrator access required.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view
