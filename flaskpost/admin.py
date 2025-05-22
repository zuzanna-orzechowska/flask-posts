from flask import Blueprint, render_template, g, redirect, url_for, flash
from flaskpost.auth import admin_required
from flaskpost.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def index():
    r = get_db()

    user_ids = r.lrange("user_ids", 0, -1)
    users = []
    for uid in user_ids:
        user_data = r.hgetall(f"user:{uid}")
        user_data['id'] = uid
        users.append(user_data)

    post_ids = r.lrange("post_ids", 0, -1)
    posts = []
    for pid in post_ids:
        post_data = r.hgetall(f"post:{pid}")
        post_data['id'] = pid
        posts.append(post_data)

    return render_template('admin/index.html', users=users, posts=posts)

@bp.route('/delete-user/<user_id>')
@admin_required
def delete_user(user_id):
    r = get_db()
    r.delete(f"user:{user_id}")
    r.lrem("user_ids", 0, user_id)
    flash('User deleted.')
    return redirect(url_for('admin.index'))

@bp.route('/delete-post/<post_id>')
@admin_required
def delete_post(post_id):
    r = get_db()
    r.delete(f"post:{post_id}")
    r.lrem("post_ids", 0, post_id)
    flash('Post deleted.')
    return redirect(url_for('admin.index'))
