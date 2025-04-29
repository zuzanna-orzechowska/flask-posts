import os
from flask import Flask

def create_app(test_config=None): #application factory function
    app = Flask(__name__, instance_relative_config=True) #creating Flask instance -arg: current module name, config files are relative to the instance folder
    app.config.from_mapping(
        SECRET_KEY='dev', #setting key to keep data safe
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), #path to database
    )

    if test_config is None:
        #load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/') #main route
    def hello():
        return 'Hello, World!'
    
    from . import db
    db.init_app(app)

    return app

