import sqlite3
from datetime import datetime

import click
from flask import current_app, g #g stores data that can be accessed by multiple functions

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row #allows accessing columns by name

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() #checks if connwction was created by checking if g.db was set

#handling database connection
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f: #opens file relative to flaskpost package
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

#registering with application instance
def init_app(app):
    app.teardown_appcontext(close_db) #calls close_db when the app context is popped
    app.cli.add_command(init_db_command)

