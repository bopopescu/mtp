from flask import Flask
import multiprocessing
# from flask.ext.mail import Mail
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask import Blueprint
from flask_socketio import SocketIO
from flask_redis import Redis
from config import config
from redis import StrictRedis
# from .testcase.manager import supportManager as hahahManager

bootstrap=Bootstrap()
# mail=Mail()
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view='auth.login'
def ttt():
    while True:
        print ('ttt')
        time.sleep(3)


p=multiprocessing.Process(target=ttt)
p.daemon=True
p.start()

class DecodedRedis(StrictRedis):
    @classmethod
    def from_url(cls, url, db=None, **kwargs):
        kwargs['decode_responses'] = True
        return StrictRedis.from_url(url, db, **kwargs)


redis = Redis.from_custom_provider(DecodedRedis)
socketio=SocketIO()
# from .manager import manager,supportManager
# mmm=hahahManager()
def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    # mail.init_app(app)
    db.init_app(app)
    redis.init_app(app)
    socketio.init_app(app,async_mode='eventlet')
    login_manager.init_app(app)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')
    
    from .testcase import testcase as testcase_blueprint
    app.register_blueprint(testcase_blueprint,url_prefix='/testcase')
    # from .monitor import monitor as monitor_blueprint
    # app.register_blueprint(monitor_blueprint,url_prefix='/monitor')
    # from .operation import operation as operation_blueprint
    # app.register_blueprint(operation_blueprint,url_prefix='/operation')

    return app

