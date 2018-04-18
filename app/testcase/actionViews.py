from . import testcase,m,sidWithSerialMap,cacheMap2
from .. import socketio
from flask import request
from flask_socketio import emit
from flask.ext.login import login_required,login_user,current_user,logout_user
from . import db
#minicap control
def errorhandler(errorinfo):
    print ('fuckerror',errorinfo)
    emit('actionRes',{'result':'error','msg':errorinfo})


def associate_address_with_sid(sid,serial):
    if sidWithSerialMap.get(sid):
        sidWithSerialMap[sid].append(serial)
    else:
        sidWithSerialMap[sid]=[serial]
def get_serials_from_sid(sid):
    if sidWithSerialMap.get(sid):
        return sidWithSerialMap.pop(sid)
    else:
        return []
def remove_serial_from_sid(sid,serial):
    if sidWithSerialMap.get(sid):
        serials=sidWithSerialMap[sid]
        if len(serials)>1:
            if serial in serials:
                sidWithSerialMap[sid].remove(serial)
        else:
            sidWithSerialMap.pop(sid)


@socketio.on('disconnect',namespace='/action')
def screen_disconnect():
    print ('disconnect',request.sid)
    serials=get_serials_from_sid(request.sid)
    if serials:
        for serial in serials:
            if not m.stopCap(serial):
                errorhandler('stopCap error')
            else:
                db.setDeviceAvailable(serial,current_user.id)
                socketio.emit('change','hehe',namespace='/default')          
                print ('screen disconnect remove %s to %s'%(serial,request.sid))


@socketio.on('onscreen',namespace='/action')
def screen_on(json):
    print ('onscreen',request.sid)
    serial=json['serial']
    if not m.startCap(json['serial'],current_user):
        errorhandler('startCap error')
    else:
        db.setDeviceBusy(serial,current_user.id,current_user.username)
        socketio.emit('change','hehe',namespace='/default')
        associate_address_with_sid(request.sid,serial)
        print ('onscreen set %s to %s'%(serial,request.sid))              

    # serial=json['serial']
    # requestSid=cacheMap2.get(serial)
    # if requestSid:
    #     emit('onscreenerror',room=requestSid,namespace='/action')
    # if not m.startCap(json['serial'],current_user):
    #     errorhandler('startCap error')
    # else:
    #     db.setDeviceBusy(serial,current_user.id,current_user.username)
    #     socketio.emit('change','hehe',namespace='/default')
    #     cacheMap[request.sid]=serial
    #     cacheMap2[serial]=request.sid
    #     print ('onscreen set %s to %s'%(serial,request.sid))


@socketio.on('disconnect',namespace='/default')
def handlerdisconnect():
    print ('default disconnect',request.sid)


@socketio.on('offscreen',namespace='/action')
def screen_off(json):
    serial=json['serial']
    remove_serial_from_sid(request.sid,serial)
    if not m.stopCap(json['serial']):
        errorhandler('stopCap error')
    else:
        db.setDeviceAvailable(serial,current_user.id)
        socketio.emit('change','hehe',namespace='/default')
        # associate_address_with_sid(request.sid,serial)
        print ('offscreen',json)
        # cacheMap.pop(request.sid)
        # cacheMap2.pop(json['serial'])

@socketio.on('closescreen',namespace="/default")
def screen_close(json):
    serial=json['serial']
    print ('closescreen',json) 
    if not m.stopCap(json['serial']):
        errorhandler('stopCap error')
    else:
        print ('set avaliable')
        db.setDeviceAvailable(serial,current_user.id)
        socketio.emit('change','hehe',namespace='/default')
        # associate_address_with_sid(request.sid,serial)
        # cacheMap.pop(request.id)
        # cacheMap2.pop(json['serial'])
   



@socketio.on('offabc',namespace='/action')
def screen_abc(json):
    pass

@socketio.on('size',namespace='/action')
def screen_size(json):
    if not m.updateConfig(json['serial'],json['x'],json['y']):
        errorhandler('size error')
    print ('screen size',json['x'],json['y'])
@socketio.on('rotation',namespace='/action')
def screen_rotation(json):
    if not m.updateRotation(json['serial'],json['rotation']):
        errorhandler('rotation error')
    print ('screen rotation',json['rotation'])




#keyPress
@socketio.on('keyPress',namespace='/action')
def keyPressHandler(json):
    a=m.sendServices(json['key'],'keyPress',json['data'])
@socketio.on('keyUp',namespace='/action')
def keyUpHandler(json):
    a=m.sendServices(json['key'],'keyUp',json['data'])
@socketio.on('keyDown',namespace='/action')
def keyDownHandler(json):
    a=m.sendServices(json['key'],'keyDown',json['data'])
@socketio.on('type',namespace='/action')
def typeHandler(json):
    print (json)
    a=m.sendServices(json['key'],'type',json['data'])
@socketio.on('wake',namespace='/action')
def wakeHandler(json):
    a=m.sendServices(json['key'],'wake',json['data'])
@socketio.on('rotate',namespace='/action')
def rotateHandler(json):
    a=m.sendServices(json['key'],'rotate',json['data'])
@socketio.on('getProperties',namespace='/action')
def getPropertiesHandler(json):
    a=m.sendServices(json['key'],'getProperties',json['data'])
@socketio.on('GetBrowsersRequest',namespace='/action')
def GetBrowsersRequestHandler(json):
    a=m.sendServices(json['key'],'GetBrowsersRequest',json['data'])
@socketio.on('setlockStatue',namespace='/action')
def setlockStatueHandler(json):
    a=m.sendServices(json['key'],'setlockStatue',json['data'])


#touch
@socketio.on('gestureStart',namespace='/action')
def gestureStartHandler(json):
    if json['key']:
        m.sendTouchs(json['key'],'gestureStart',json['data'])
@socketio.on('gestureStop',namespace='/action')
def gestureStopHandler(json):
    m.sendTouchs(json['key'],'gestureStop',json['data'])
@socketio.on('touchDown',namespace='/action')
def touchDownHandler(json):
    m.sendTouchs(json['key'],'touchDown',json['data'])
@socketio.on('touchUp',namespace='/action')
def touchUpHandler(json):
    m.sendTouchs(json['key'],'touchUp',json['data'])
@socketio.on('touchMove',namespace='/action')
def touchMoveHandler(json):
    m.sendTouchs(json['key'],'touchMove',json['data'])
@socketio.on('touchCommit',namespace='/action')
def touchCommitHandler(json):
    m.sendTouchs(json['key'],'touchCommit',json['data'])
@socketio.on('touchReset',namespace='/action')
def touchResetHandler(json):
    m.sendTouchs(json['key'],'touchReset',json['data'])