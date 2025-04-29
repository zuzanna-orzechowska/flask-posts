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
    
    from . import db
    db.init_app(app)

    #blueprint for authentucation
    from . import auth
    app.register_blueprint(auth.bp)

    #blueprint for blog
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import admin
    app.register_blueprint(admin.bp)


    return app

