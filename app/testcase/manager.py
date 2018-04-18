from .minicap import *
from .minitouch import *
from .services import stfServices
from .adbkit import *
from . import db
from .ConnectDevice import ConnectScreenCap
from eventlet.queue import Queue
import time
import eventlet

# from Queuee import Queue as q
eventlet.monkey_patch()


class supportManager():
	def __init__(self):
		self.minicap_clients={}
		self.minitouch_clients={}
		self.stfservice_clients={}
		self.init_portlist()

	def init_portlist(self):
		self.minicap_q=Queue(50)
		self.minitouch_q=Queue(50)
		self.stfservices_q=Queue(50)
		for port in range(1300,1350):
			self.minicap_q.put(port)
			self.minitouch_q.put(port-100)
		for port in range(1100,1190,2):
			self.stfservices_q.put(port)

	def _getPort(self,type):
		if type=='minicap':
			return self.minicap_q.get()
		elif type=='minitouch':
			return self.minitouch_q.get()
		else:
			return self.stfservices_q.get()

	def register_minicap(self,serial,minicap_port,deviceInfos):
		self.minicap_clients[serial]=Minicap(('localhost',minicap_port),serial,deviceInfos)

	def register_minitouch(self,serial,minitouch_port,deviceInfos):
		self.minitouch_clients[serial]=Minitouch(('localhost',minitouch_port),serial,deviceInfos)

	def register_stfservice(self,serial,stfservice_port):
		self.stfservice_clients[serial]=stfServices(('localhost',stfservice_port),serial)
		
	def checkDeviceAvaliable(self,serial):
		touch_client=self.minitouch_clients.get(serial)
		service_client=self.stfservice_clients.get(serial)
		if not touch_client or not service_client:
			return False
		if touch_client.runningState!=3 and touch_client.runningState!=3:
			# print ('not starting',serial,touch_client.runningState,touch_client.runningState)
			return False
		return True

	def init2(self,serial):
		deviceInfos=get_deviceInfo(serial)

		if not deviceInfos:
			db.setDeviceError(serial)
			socketio.emit('change','hehe',namespace='/default')
			return
		stfservice_port=self._getPort('stfservice')
		self.register_stfservice(serial,stfservice_port)
		self.stfservice_clients[serial].init()
		self.stfservice_clients[serial].start()
		self.stfservice_clients[serial].getProperties('haha')
		if not self.stfservice_clients[serial].app:
			db.setDeviceError(serial)
			socketio.emit('change','hehe',namespace='/default')
			return

		minitouch_port=self._getPort('minitouch')
		self.register_minitouch(serial,minitouch_port,deviceInfos)
		self.minitouch_clients[serial].init()
		self.minitouch_clients[serial].start()
		if self.minitouch_clients[serial].pid<=0:
			db.setDeviceError(serial)
			socketio.emit('change','hehe',namespace='/default')
			return

		minicap_port=self._getPort('minicap')
		self.register_minicap(serial,minicap_port,deviceInfos)
		displayinfos=self.minicap_clients[serial].init()


		db.setDeviceReady(serial)
		db.setDeviceInfo(serial,{'minicap_port':minicap_port,'minitouch_port':minitouch_port})
		socketio.emit('change','hehe',namespace='/default')

		deviceInfos['display']=displayinfos

		if self.stfservice_clients[serial].phone:
			tempd={}
			for i in self.stfservice_clients[serial].phone:
				tempd[i.name]=i.value
			deviceInfos['phone']=tempd
		db.setDeviceInfo(serial,deviceInfos)

		socketio.emit('change','hehe',namespace='/default')
	def init(self,serial):
		eventlet.spawn_n(self.init2,serial)

	def startCap(self,key,current_user):
		try:
			if not self.checkDeviceAvaliable(key):
				return 0
			minicap_client=self.minicap_clients.get(key)
			res=minicap_client.start()
			# db.setDeviceBusy(serial,current_user.id,current_user.username)
			# socketio.emit('change','hehe',namespace='/default')
			return 1
		except Exception as e:
			print ('Cap_start Error',str(e))
			return 0

	def updateConfig(self,key,width,height):
		try:
			if not self.checkDeviceAvaliable(key):
				return 0
			minicap_client=self.minicap_clients.get(key)
			minicap_client.updateConfig(width,height)
			return 1
		except Exception as e: 
			print ('Cap_updataConfig Error',str(e))
			return 0

	def updateRotation(self,key,rotation):
		try:
			if not self.checkDeviceAvaliable(key):
				return 0
			minicap_client=self.minicap_clients.get(key)
			minicap_client.updateRotation(rotation)
			return 1
		except:
			print ('Cap_updataConfig Error')
			return 0

	def stopCap(self,key):
		try:
			r=self.minicap_clients.get(key)
			res=r.stop()
			return 1
		except:
			print ('Cap_stop Error')
			return 0

	def startTouch(self,key):
		r=self.minitouch_clients.get(key)
		if r:
			t=r.get('touch')
			if t:
				res=t.start()
				# print (res,'touch start')
				return 1
			else:
				# print ('%s[touch] client not found'%key)
				return 0
		else:
			# print ('%s not found')
			return 0
	def startServices(self,key):
		r=self.stfservice_clients.get(key)
		if r:
			t=r.get('stf')
			if t:
				res=t.start()
				return 1
			else:
				return 0
		else:
			return 0
	def closeAll(self,key):
		touch_client=self.minitouch_clients.get(key)
		stf_client=self.stfservice_clients.get(key)
		cap_client=self.minicap_clients.get(key)
		if cap_client:
			print ('cap',cap_client.close())
		if touch_client:
			t=touch_client.get('touch')
			if t:
				# t.close()
				print ('touch',t.close())
		if stf_client:
			s=stf_client.get('stf')
			if s:
				print ('services',s.close())
		self.minitouch_clients.pop(key)
		self.stfservice_clients.pop(key)
		self.minicap_clients.pop(key)
		del touch_client
		del stf_client
		del cap_client
		return 1	
	def sendTouch(self,key,action,data):
		r=self.minitouch_clients.get(key)
		if r:
			eval('r.%s(data)'%action)
			return 1
		else:
			return 0
	def sendService(self,key,type_t,data):
		r=self.stfservice_clients.get(key)
		if r:
			eval('r.%s(data)'%type_t)
			return 1
		else:
			return 0

	def sendTouchs(self,keys,action,data):
		for k in keys:
			self.sendTouch(k,action,data)
	def sendServices(self,keys,type_t,data):
		for k in keys:
			self.sendService(k,type_t,data)

