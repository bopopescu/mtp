from . import testcase,m
from .. import socketio
from . import db
# from .provider import Provider
from flask import request,jsonify
import os,json,time
from flask.ext.login import login_required,login_user,current_user,logout_user
from flask_socketio import join_room, leave_room, close_room,send,emit
import eventlet
# class Provider():
#     def __init__(self):
#         self.default_check_count=0
#         self.temp=[]
#     def loop(self):
#         while True:
#             st=time.time()
#             d=get_devices()
#             if d is None:
#                 print ('error adbkit')
#                 continue
#             current_all_devices=list(d.keys())
#             if self.temp!=current_all_devices:
#                 print ('currentDevices',self.temp)
#                 print ('targetDevices',current_all_devices)
#                 new_devices=list(set(current_all_devices).difference(set(self.temp)))
#                 remove_devices=list(set(self.temp).difference(set(current_all_devices)))
#                 print (self.temp,current_all_devices,new_devices,remove_devices)
#                 t=threading.Thread(target=self.device_update,args=(new_devices,remove_devices))
#                 t.setDaemon(True)
#                 t.start()
#                 self.temp=current_all_devices
#             elif self.default_check_count>3000:
#                 t=threading.Thread(target=self.device_default_check,args=(current_all_devices,))
#                 t.setDaemon(True)
#                 t.start()
#                 self.default_check_count=0
#             time.sleep(0.3)
#             self.default_check_count+=1
#     def device_update(self,new_devices,remove_devices):
#         print (new_devices,remove_devices,'update')
#         if new_devices:
#             try:
#                 r=requests.post('http://10.1.58.68:7777/testcase/adddevices',data={'infos':json.dumps(new_devices)},timeout=(0.5,8.5))
#                 print (new_devices,'new')
#             except Exception as e:
#                 self.temp=[]
#                 print ('add error:%s'%str(e))
#         if remove_devices:
#             try:
#                 r=requests.post('http://10.1.58.68:7777/testcase/removedevices',data={'infos':json.dumps(remove_devices)},timeout=(0.5,1.5))
#                 print (remove_devices,'remove')
#             except:
#                 self.temp=[]
#                 print ('remove error')
#             # print (remove_devices,'remove')
#         # time.sleep(3)
#     def device_default_check(self,all_devices):
#         print (all_devices,'defaultCheck')
#         try:
#             r=requests.post('http://10.1.58.68:7777/testcase/devicecheck',data={'infos':json.dumps(all_devices)},timeout=(0.5,3.5))
#         except Exception as e:
#             print ('default_check_error',str(e))
def backgroundTask():
    while True:
        print ('haha')
        time.sleep(10)


def sentCurrentDevices():
	infos=db.getAllDevices(current_user.id)
	# print (infos['fa3fb4067d52']['status'],current_user.id)
	emit('update',infos)

@socketio.on('connect', namespace='/default')
def test_connect2():
    print ('connect default',request.sid)
    sentCurrentDevices()   

@socketio.on('getInfos', namespace='/default')
def getInfos(data):
    sentCurrentDevices() 


# @socketio.on('getDeviceStatus',namespace='/default')
@testcase.route('/getDeviceStatus',methods=['GET'])
def getDeviceStatus():
	serials=db.getAllDeviceSerials()
	d={}
	for serial in serials:
		d[serial]=m.checkDeviceAvaliable(serial)
	return jsonify(d)

# @testcase.route('/adddevices',methods=['POST'])
# def recv_deviceinfo():
#     devices=request.form.get('infos')
#     devices=json.loads(devices)
#     db.addDevices(devices)
#     for serial in devices:
#         print ('add',serial)
#         ports=m.init(serial)
#     socketio.emit('change','hehe',namespace='/default')
#     return 'success'

# @testcase.route('/removedevices',methods=['POST'])
# def remove_devices():
#     st=time.time()
#     devices=request.form.get('infos')
#     devices=json.loads(devices)
#     print (devices)
#     db.removeDevices(devices)
#     socketio.emit('change','hehe',namespace='/default')
#     print (time.time()-st,'remove')
#     return 'success'

# @testcase.route('/devicecheck',methods=['POST'])
# def default_devices():
#     return 'success'