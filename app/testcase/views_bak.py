import eventlet,time  
# eventlet.monkey_patch(socket=True, select=True)
from flask import render_template,redirect,flash,request,url_for,jsonify,current_app,copy_current_request_context,session
from flask.ext.login import login_required,login_user,current_user,logout_user
from . import testcase,m
import datetime
from flask.ext.login import current_user,login_required
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
# db.initDevices()
# m=supportManager()
cacheMap={}
cacheMap2={}

@socketio.on('disconnect',namespace='/action')
def screen_disconnect():
    serial=cacheMap.get(request.sid)
    if serial:
        if not m.stopCap(serial):
            errorhandler('stopCap error')
        else:
            db.setDeviceAvailable(serial,current_user.id)
            socketio.emit('change','hehe',namespace='/default')       
            cacheMap.pop(request.sid)
            cacheMap2.pop(serial)
            print ('screen disconnect remove %s to %s'%(serial,request.sid))

@socketio.on('onscreen',namespace='/action')
def screen_on(json):
    serial=json['serial']
    requestSid=cacheMap2.get(serial)
    if requestSid:
        emit('onscreenerror',room=requestSid,namespace='/action')
    if not m.startCap(json['serial'],current_user):
        errorhandler('startCap error')
    else:
        db.setDeviceBusy(serial,current_user.id,current_user.username)
        socketio.emit('change','hehe',namespace='/default')
        cacheMap[request.sid]=serial
        cacheMap2[serial]=request.sid
        print ('onscreen set %s to %s'%(serial,request.sid))
@socketio.on('offscreen',namespace='/action')
def screen_off(json):
    if not m.stopCap(json['serial']):
        errorhandler('stopCap error')
    else:
        db.setDeviceAvailable(json['serial'],current_user.id)
        socketio.emit('change','hehe',namespace='/default')
        print ('offscreen',json)
        cacheMap.pop(request.sid)
        cacheMap2.pop(json['serial'])

@socketio.on('closescreen',namespace="/default")
def screen_close(json):
    print ('closescreen',json) 
    if not m.stopCap(json['serial']):
        errorhandler('stopCap error')
    else:
        print ('set avaliable')
        db.setDeviceAvailable(json['serial'],current_user.id)
        socketio.emit('change','hehe',namespace='/default')
        cacheMap.pop(request.id)
        cacheMap2.pop(json['serial'])


def sendf():
    while True:
        socketio.emit('heihei','heihei1',room=1,namespace='/default')
        socketio.emit('heihei','heihei2',room=2,namespace='/default')
        time.sleep(1)
def sentCurrentDevices():
    socketio.emit('update',db.getAllDevices(),namespace='/default')


@socketio.on('connect', namespace='/default')
def test_connect2():
    sentCurrentDevices()   

@socketio.on('getInfos', namespace='/default')
def getInfos(data):
    sentCurrentDevices() 

@testcase.route('/adddevices',methods=['POST'])
def recv_deviceinfo():
    st=time.time()
    devices=request.form.get('infos')
    devices=json.loads(devices)
    db.addDevices(devices)
    for serial in devices:
        ports=m.init(serial)
    socketio.emit('change','hehe',namespace='/default')
    # socketio.emit('update',sorted(db.getAllDevices().items(),key=lambda asd:asd[1],reverse=True),namespace='/default')
    print (time.time()-st,'add')
    return 'success'
@testcase.route('/removedevices',methods=['POST'])
def remove_devices():
    st=time.time()
    devices=request.form.get('infos')
    devices=json.loads(devices)
    print (devices)
    db.removeDevices(devices)
    socketio.emit('change','hehe',namespace='/default')
    print (time.time()-st,'remove')
    return 'success'
@testcase.route('/devicecheck',methods=['POST'])
def default_devices():
    return 'success'


def gettoken(id,serial):
    return 'fff'+str(id)+str(serial)

@testcase.route('/connect')
def connect():
    # return 'dasdadadad'
    # print ('haha')
    try:
        deviceInfos=get_deviceInfo('fa3fb4067d52')
        c=ConnectScreenCap('fa3fb4067d52',deviceInfos)
        # ConnectScreenCap.forward_minicap(1313)
        c.connect_cap(1313)
        c.connect_touch(1111)
        c.connect_service((1100,1090))
        print ('fuc2k')
    except Exception as e:
        return 'error:%s'%str(e)
    return 'hahaha'

@testcase.route('/detail')
@login_required
def detail():
    timestamp=request.args.get('timestamp')
    key=request.args.get('key')
    sign=request.args.get('sign')
    serial=request.args.get('serial')
    # print (request.sid,'r2f2f2f2f2f2f2f2f2f2')
    if checkhash(timestamp,key,sign):
        uid=current_user.id
        # db.setDeviceBusy(serial,current_user.username)
        # print (m.startCap(serial),current_user.id,'screen connected')
        # print (m.startTouch(serial),current_user.id,'touch connected')
        # print (m.startServices(serial),current_user.id,'services connected')
        # print (m.add(uid,('localhost',1313)),'add')
        return render_template('testcase/detail.html')
    else:
        print ('fad')
        return redirect(url_for('testcase.index'))


@testcase.route('/jump')
@login_required
def jump():
    serial=request.args.get('serial')
    print (serial,'serial')
    # print (request.sid,'r2f2f2f2f2f2f2f2f2f2')
    # join_room(serial)
    if request.headers.get('Referer'):
        timestamp=int(time.time()*1000)
        key='secretkey'
        sign=gethash(timestamp,key)
        uid=current_user.id
        token=gettoken(uid,serial)
        return redirect(url_for('testcase.detail',timestamp=timestamp,key=key,sign=sign,uid=uid,token=token,serial=serial))
    else:
        return redirect(url_for('testcase.index'))

@testcase.route('/index')
@login_required
def index():
    # print (m.keys(),'keys')
    return render_template('testcase/index.html')
@testcase.route('/testdata')
def testdata():
    socketio.emit('testdata','testtest',namespace='/screen')
    return 'sucess'

# @socketio.on('connect')
# def test_connect():
#     print ('client connected')
# @socketio.on('disconnect')
# def test_connect():
#     print ('client disconnected')
# @socketio.on('connect', namespace='/screen')
# def test_connect():
#     print ('test_connect')
#     print (request,'rrrrrrrrrrrrr',request.sid)
    # print (m.startCap('fa3fb4067d52'),current_user.id,'screen connected')
    # print (m.startTouch('fa3fb4067d52'),current_user.id,'touch connected')
    # print (m.startServices(current_user.id),current_user.id,'services connected')

# @socketio.on('disconnect', namespace='/screen')
# def test_disconnect():
#     print ('close message')
    # print (m.closeAll(current_user.id),current_user.id,'screen disconnected')

@socketio.on('join',namespace='/default')
def on_join(data):
    print ('join room')
    # username = data['username']
    # room = data['room']
    join_room(1)
    # send(username + ' has entered the room.', room=room)

@socketio.on('leave',namespace='/default')
def on_leave(data):
    print ('leave room')
    # username = data['username']
    # room = data['room']
    leave_room(1)
    # send(username + ' has left the room.', room=room)




@testcase.route('/stop')
@login_required
def stop():
    uid=current_user.id
    t=m.closeAll(uid)
    if t:
        print ('success')
        return jsonify(status=1)
    else:
        print ('failed')
        return jsonify(status=2)


@testcase.route('/upload',methods=['POST'])
@login_required
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

# # @socketio.on('up')
# # def handle_my_custom_event2(json):
# #     s="u 0\n"
# #     s=s.encode('ascii')
# #     sq.put(s)
# #     sq.put("c\n".encode('ascii'))
# #     print ('up',sq.qsize())
def installApk(apkPath):
    print ('iamin')
    emit('res',{'c':1})
    return

    try:
        packageName=getpackage(apkPath)
        activity=getActivity(apkPath)
    except:
        emit('res','get package failed')
        print ('get package failed')
    try:
        res2=install('fa3fb4067d52','/tmp/uploadforder/20160530-baidu-release.apk')
        if res2[1][2]!='Success':
            emit('res','install failed')
            print ('install failed')
        else:
            emit('res','install success')
            print ('install success')
        res=launchApp(p,a)
        if res.startwith('Starting'):
            emit('res','launch success')
            print ('launch success')
        else:
            emit('res','launch failed')
    except:
        emit('res','install failed')
def aaa(message):
    emit('res',{'c':1})
    emit('res',{'e':1},broadcast=True)
    socketio.emit('res',{'d':1},namespace='/screen')
@socketio.on('install',namespace='/screen')
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
            res2=install('fa3fb4067d52',os.path.join(current_app.config['UPLOAD_FOLDER'],apkPath))
            if res2[1][2]!='Success':
                emit('installResponse',{'data':'install failed','result':'fail','id':id})
                print ('install failed')
                return
            else:
                emit('installResponse',{'data':'98%','result':'success','id':id})
                print ('install success')
            print (packageName,activity)
            res=launchApp(packageName,activity)
            if res.startswith('Starting'):
                emit('installResponse',{'data':'100%','result':'success','id':id,'packageName':packageName,'activity':activity,'version':version})
                print ('launch success')
            else:
                emit('installResponse',{'data':'launch failed','result':'fail','id':id})
                print (res)
                return
        except Exception as e:
            emit('installResponse',{'data':'install failed2','result':'fail','id':id})
    eventlet.spawn_n(installApk,message['path'],message['id'])
    # haha2(os.path.join(current_app.config['UPLOAD_FOLDER'],message['path']))
    print ('fuckdone')
    # aaa(message)
@socketio.on('uninstall',namespace='/screen')
def uninstallhandler(message):
    print ('uninstall',message['packageName'])
    def uninstallApk(packageName):
        uninstall('fa3fb4067d52',packageName)
    eventlet.spawn_n(uninstallApk,message['packageName'])



@socketio.on('onab',namespace='/screen')
def screen_on(json):
    print ('onab',request.sid)
    ser=cacheMap2.get(json['serial'])
    if ser:
        print ('send avcdefasdadsfskfjaklfjafkljfa')
        socketio.emit('abcdedg',room=ser,namespace='/screen')
        m.stopCap(json['serial'])
        cacheMap.pop(ser)
        cacheMap2.pop(json['serial'])       
    join_room('thefuck')
    m.startCap(json['serial'])
    cacheMap[request.sid]=json['serial']
    cacheMap2[json['serial']]=request.sid
    print ('screen on')

@socketio.on('offab',namespace='/screen')
def screen_off(json):
    leave_room('thefuck')
    m.stopCap(json['serial'])
    print ('screen disconnect',json)

@socketio.on('offabc',namespace='/screen')
def screen_off(json):
    # leave_room('thefuck')
    # m.stopCap(json['serial'])
    print (json['a']*10)

@socketio.on('size',namespace='/screen')
def screen_size(json):
    m.updateConfig(json['serial'],json['x'],json['y'])
    print ('screen size',json['x'],json['y'])
@socketio.on('rotation',namespace='/screen')
def screen_rotation(json):
    m.updateRotation(json['serial'],json['rotation'])
    print ('screen rotation',json['rotation'])
# @socketio.on('connect',namespace='/screen')
# def screen_disconnect():
#     m.startCap('fa3fb4067d52')
#     print ('screen connect')
@socketio.on('disconnect',namespace='/screen')
def screen_disconnect():
    # leave_room('thefuck')
    ser=cacheMap.get(request.sid)
    if ser:
        leave_room('thefuck') 
        m.stopCap(ser)
        cacheMap.pop(request.sid)
        cacheMap2.pop(ser)
    print (request.namespace,request.namespace,request.sid)
    print (session)
    print ('screen disconnect')




# @socketio.on('connect', namespace='/chat')
# def test_connect():    
#     emit('connect response', {'result': 'Connected','result':1})

