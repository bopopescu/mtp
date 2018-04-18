from . import  login_manager
from . import db
from datetime import datetime
# from .auth.auth_crowd import auth_crowd

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    displayname=db.Column(db.String(64))
    email=db.Column(db.String(64),index=True)
    groups=db.Column(db.String(256))
    phone=db.Column(db.String(64))
    def is_authenticated(self):
	    return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id

class UiTask(db.Model):
    __tablename__='uitask'
    id=db.Column(db.Integer,primary_key=True)
    cport=db.Column(db.Integer,primary_key=True)
    bport=db.Column(db.Integer)
    logpath=db.Column(db.String(64))
    uid=db.Column(db.Integer,primary_key=True)
    status=db.Column(db.Integer,primary_key=True)
    devicename=db.Column(db.String(32))

# class Devices(db.Model):
#     __tablename__='deviceinfo'
#     id=db.Column(db.Integer,primary_key=True)
#     serial=db.Column(db.String(64),unique=True,index=True)
#     status=
