import eventlet,time  
# eventlet.monkey_patch(socket=True, select=True)
from flask import render_template,redirect,flash,request,url_for,jsonify,current_app,copy_current_request_context,session
from flask.ext.login import login_required,login_user,current_user,logout_user
from . import testcase,m
import datetime
from ..models import User,UiTask
# from .testa import init
from .testc import init2
from .. import socketio
# from .manager import manager,supportManager
from .hashcheck import gethash,checkhash
from eventlet.queue import Queue
from .ConnectDevice import ConnectScreenCap
from .installHelper import *
from .adbkit import *
import os,json
from . import db
from flask_socketio import join_room, leave_room, close_room,send,emit
from werkzeug import secure_filename


@testcase.route('/getDeviceList')
def getDeviceList():
	eleid=request.args.get('eleid')
	deviceslist=db.getAvaliableDevices()
	return render_template('testcase/deviceList.html',results=deviceslist,eleid=eleid)

@testcase.route('/addDeviceView')
def addDeviceView():
	try:
		serial=request.args.get('serial')
		infos=db.getDeviceInfos(serial)
		infos['display']=eval(infos['display'])
	except:
		print (infos)
	return jsonify(infos)



@testcase.route('/multi')
def multi():
	return render_template('testcase/multi.html')



