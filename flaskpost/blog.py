from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
from datetime import datetime

from flaskpost.auth import login_required
from flaskpost.db import get_db
from redisdb import r

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    r = get_db()
    post_ids = r.lrange("post_ids", 0, -1)  # od najnowszego do najstarszego
    posts = []
    for pid in post_ids:
        post_data = r.hgetall(f"post:{pid}")
        if post_data:
            posts.append({
                "id": pid,
                "title": post_data['title'],
                "body": post_data['body'],
                "created": post_data['created'],
                "author_id": post_data['author_id'],
                "username": post_data['username'],
            })
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            r = get_db()
            post_id = r.incr("next_post_id")
            now = datetime.utcnow().isoformat()
            r.hset(f"post:{post_id}", {
                "title": title,
                "body": body,
                "author_id": g.user['id'],
                "username": g.user['username'],
                "created": now
            })
            r.rpush("post_ids", post_id)
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    r = get_db()
    post_data = r.hgetall(f"post:{id}")
    if not post_data:
        abort(404, f"Post id {id} doesn't exist.")
    post = {
        "id": id,
        "title": post_data['title'],
        "body": post_data['body'],
        "created": post_data['created'],
        "author_id": post_data['author_id'],
        "username": post_data['username']
    }
    if check_author and post["author_id"] != g.user['id']:
        abort(403)
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(str(id))

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            r = get_db()
            r.hset(f"post:{id}", {
                "title": title,
                "body": body,
                "author_id": post["author_id"],
                "username": post["username"],
                "created": post["created"]
            })
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(str(id))
    r = get_db()
    r.delete(f"post:{id}")
    r.lrem("post_ids", 0, id)
    return redirect(url_for('blog.index'))
