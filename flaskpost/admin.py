from flask import Blueprint, render_template, g, redirect, url_for, flash
from flaskpost.auth import admin_required
from flaskpost.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@admin_required
def index():
    db = get_db()
    users = db.execute('SELECT id, username, is_admin FROM user').fetchall()
    posts = db.execute('SELECT id, title FROM post').fetchall()
    return render_template('admin/index.html', users=users, posts=posts)

@bp.route('/delete-user/<int:user_id>')
@admin_required
def delete_user(user_id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()
    flash('User deleted.')
    return redirect(url_for('admin.index'))

@bp.route('/delete-post/<int:post_id>')
@admin_required
def delete_post(post_id):
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()
    flash('Post deleted.')
    return redirect(url_for('admin.index'))
