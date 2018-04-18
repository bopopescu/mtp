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
# eventlet.monkey_patch()
db.initDevices()


def gettoken(id,serial):
    return 'fff'+str(id)+str(serial)




# @testcase.route('/detail')
# @login_required
# def detail():
#     timestamp=request.args.get('timestamp')
#     key=request.args.get('key')
#     sign=request.args.get('sign')
#     serial=request.args.get('serial')
#     if not db.isDeviceStatus(serial,'ready'):
#         flash('%s is unavaliable'%serial)
#         return redirect(url_for('testcase.index'))
#     if checkhash(timestamp,key,sign):
#         uid=current_user.id

#         return render_template('testcase/detail.html')
#     else:
#         # print ('fad')
#         flash('非法请求2')
#         return redirect(url_for('testcase.index'))
@testcase.route('/detail')
def detail2():
    serial=request.args.get('serial')
    uid=current_user.id
    if db.isDeviceStatus(serial,'ready') or str(uid)==db.getDeviceCurrentUser(serial):
        return render_template('testcase/detail.html')
    else:
        flash('当前设备使用中-%s-%s'%(db.getDeviceCurrentUser(serial),uid))
        return redirect(url_for('testcase.index'))
# @testcase.route('/jump')
# @login_required
# def jump():
#     serial=request.args.get('serial')
#     if request.headers.get('Referer'):
#         timestamp=int(time.time()*1000)
#         key='secretkey'
#         sign=gethash(timestamp,key)
#         uid=current_user.id
#         token=gettoken(uid,serial)
#         if not db.isDeviceStatus(serial,'ready'):
#             flash('%s is unavaliable'%serial)
#             return redirect(url_for('testcase.index'))
#         return redirect(url_for('testcase.detail',timestamp=timestamp,key=key,sign=sign,uid=uid,token=token,serial=serial))
#     else:
#         flash('非法请求')
#         return redirect(url_for('testcase.index'))

@testcase.route('/index')
# @login_required
def index():
    return render_template('testcase/index.html')


@testcase.route('/stop')
# @login_required
def stop():
    uid=current_user.id
    t=m.closeAll(uid)
    if t:
        print ('success')
        return jsonify(status=1)
    else:
        print ('failed')
        return jsonify(status=2)


#install apk

@testcase.route('/upload',methods=['POST'])
# @login_required
def upload():
    print ('FILE UPLOAD******')
    try:
        file=request.files.get('file')
        if file and allowed_file(file.filename):
            filename=secure_filename(file.filename)
            filename=filename.split('.')[0]+str(int(time.time()*1000))+'.'+filename.split('.')[1]
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
    # emit('res',{'c':1})
        return jsonify({'res':filename})
    except:
        return jsonify({'res':'error'})


def allowed_file(filename):
  return '.' in filename and \
      filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

@socketio.on('install',namespace='/action')
def fuckhandler(message):
    print (message)
    @copy_current_request_context
    def installApk(apkPath,id):
        try:
            packageName=getpackage(os.path.join(current_app.config['UPLOAD_FOLDER'],apkPath)).split("name='")[1].split("'")[0]
            version=getpackage(os.path.join(current_app.config['UPLOAD_FOLDER'],apkPath)).split("versionName='")[1].split("'")[0]
            activity=getActivity(os.path.join(current_app.config['UPLOAD_FOLDER'],apkPath)).split("name='")[1].split("'")[0]
            emit('installResponse',{'data':'90%','result':'success','id':id})
        except:
            emit('installResponse',{'data':'get package failed','result':'fail','id':id})
            print ('get package failed')
            return
        try:
            res2=install(message['serial'],os.path.join(current_app.config['UPLOAD_FOLDER'],apkPath))
            if res2[1][2]!='Success':
                emit('installResponse',{'data':'install failed','result':'fail','id':id})
                print ('install failed')
                return
            else:
                emit('installResponse',{'data':'98%','result':'success','id':id})
                print ('install success')
            print (packageName,activity)
            res=launchApp(message['serial'],packageName,activity)
            if res.startswith('Starting'):
                emit('installResponse',{'data':'100%','result':'success','id':id,'packageName':packageName,'activity':activity,'version':version})
                print ('launch success')
            else:
                emit('installResponse',{'data':'launch failed','result':'fail','id':id})
                print (res)
                return
        except Exception as e:
            print (str(e))
            emit('installResponse',{'data':'install failed2','result':'fail','id':id})
    eventlet.spawn_n(installApk,message['path'],message['id'])


@socketio.on('uninstall',namespace='/action')
def uninstallhandler(message):
    print ('uninstall',message['packageName'])
    def uninstallApk(packageName):
        uninstall(message['serial'],packageName)
    eventlet.spawn_n(uninstallApk,message['packageName'])


