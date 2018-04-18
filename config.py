import os
import time
basedir=os.path.abspath(os.path.dirname(__file__))
class Config():
    SECRET_KEY="secretkey"
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    #fix sql not available error/
    SQLALCHEMY_POOL_SIZE=50
    SQLALCHEMY_POOL_RECYCLE=299
    SQLALCHEMY_POOL_TIMEOUT=20
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    CROWD_APP='testapp'
    CROWD_APPPWD='123456'
    UPLOAD_FOLDER='/tmp/uploadforder/'
    ALLOWED_EXTENSIONS=set(['apk'])

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    # CROWD_URL="http://10.2.1.12:8095/crowd/"
    CROWD_URL='http://180.150.184.115:8095/crowd/'
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://root:automation@10.2.1.67:3306/Automonitor" 
    # SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://mtp:123456@10.1.40.31:3306/mtpdb" 
    REDIS_HOST = '192.168.150.36'
    REDIS_PORT= 6379
    REDIS_DB = 0
    DECODE_RESPONSE=True
    REDIS_URL="redis://:@192.168.150.36/:6379/0"
    @classmethod
    def init_app(cls,app):
        Config.init_app(app)

class ProductionConfig(Config):
    CROWD_URL='http://180.150.184.115:8095/crowd/'
    SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://mtp:123456@10.2.1.67:3306/mtpdb" 
    # SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL')
    REDIS_HOST = '192.168.150.36'
    REDIS_PORT= 6379
    REDIS_DB = 0
    @classmethod
    def init_app(cls,app):
        Config.init_app(app)




config={'development':DevelopmentConfig,'production':ProductionConfig}
                                                                                                                                                    
