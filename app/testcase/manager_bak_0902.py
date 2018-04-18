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
		# minicap_port=self._getPort('minicap')
		# deviceInfos=get_deviceInfo(serial)
		room='thefuck'
		self.minicap_clients[serial]=Minicap(room,('localhost',minicap_port),serial,deviceInfos)
	def register_minitouch(self,serial,minitouch_port,deviceInfos):
		# minitouch_port=self._getPort('minitouch')
		# touchQ=Queue(500)
		self.minitouch_clients[serial]=Minitouch(('localhost',minitouch_port),serial,deviceInfos)
	def register_stfservice(self,serial,stfservice_port):
		# stfservice_port=self._getPort('stfservice')
		# stfQ=Queue(500)
		self.stfservice_clients[serial]=stfServices(('localhost',stfservice_port),serial)
	def register_all(self,serial):
		self.register_minicap(serial)
		self.register_minitouch(serial)
		self.register_stfservice(serial)
	# def init(self,serial):
	# 	c=ConnectScreenCap(serial)
	# 	minicap_port=self._getPort('minicap')
	# 	minitouch_port=self._getPort('minitouch')
	# 	stfservice_port=self._getPort('stfservice')
	# # 	# print ('stfserviceport',stfservice_port)
	# 	c.init_device({'minicap_port':minicap_port,'minitouch_port':minitouch_port,'stfservice_port1':stfservice_port,'stfservice_port2':stfservice_port+1})
	# 	self.register_minicap(serial,minicap_port)
	# 	self.register_minitouch(serial,minitouch_port)
	# 	self.register_stfservice(serial,stfservice_port)
	# 	return minitouch_port,minitouch_port,stfservice_port
	def init2(self,serial):
		deviceInfos=get_deviceInfo(serial)

		minitouch_port=self._getPort('minitouch')
		self.register_minitouch(serial,minitouch_port,deviceInfos)
		self.minitouch_clients[serial].init()
		self.minitouch_clients[serial].start()

		minicap_port=self._getPort('minicap')
		self.register_minicap(serial,minicap_port,deviceInfos)
		self.minicap_clients[serial].init()

		stfservice_port=self._getPort('stfservice')
		self.register_stfservice(serial,stfservice_port)
		self.stfservice_clients[serial].init()
		self.stfservice_clients[serial].start()

		db.setDeviceReady(serial)
		db.setDeviceInfo(serial,{'minicap_port':minicap_port,'minitouch_port':minitouch_port})
		socketio.emit('change','hehe',namespace='/default')
		db.setDeviceInfo(serial,get_deviceInfo(serial))
		socketio.emit('change','hehe',namespace='/default')
	def init(self,serial):
		eventlet.spawn_n(self.init2,serial)
	def init_all(self,serial):
		self.init_minicap(serial)
		self.init_minitouch(serial)
	def init_minicap(self,serial):
		client=self.minicap_clients.get(serial)
		if client:
			client.init()
			return 1
		else:
			return 0
	def init_minitouch(self,serial):
		client=self.minitouch_clients.get(serial)
		if client:
			client['touch'].init()
			return 1
		else:
			return 0
	def startCap(self,key):
		r=self.minicap_clients.get(key)
		if r:
			t=r
			if t:
				res=t.start()
				print (res,'cap start')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found'%key)
			return 0
	def updateConfig(self,key,width,height):
		r=self.minicap_clients.get(key)
		if r:
			t=r
			if t:
				res=t.updateConfig(width,height)
				print (res,'cap update')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found'%key)
			return 0
	def updateRotation(self,key,rotation):
		r=self.minicap_clients.get(key)
		if r:
			t=r
			if t:
				res=t.updateRotation(rotation)
				print (res,'cap update')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found'%key)
			return 0	
	def stopCap(self,key):
		r=self.minicap_clients.get(key)
		if r:
			t=r
			if t:
				res=t.stop()
				print (res,'cap stop')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found'%key)
			return 0
	def startTouch(self,key):
		r=self.minitouch_clients.get(key)
		if r:
			t=r.get('touch')
			if t:
				res=t.start()
				print (res,'touch start')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found')
			return 0
	def startServices(self,key):
		r=self.stfservice_clients.get(key)
		if r:
			t=r.get('stf')
			if t:
				res=t.start()
				print (res,'stfServices start')
				return res
			else:
				print ('%s[stfServices] client not found'%key)
				return 0
		else:
			print ('%s not found')
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
		# print (seq)
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













class manager():
	def __init__(self):
		self.clients={}
	def keys(self):
		return self.clients.keys()
	def add(self,key,addr):
		if self.clients.get(key):
			return -1
		else:
			try:
				c=RealtimeScreenCap(addr,key)
				q=Queue(500)
				q2=Queue(500)
				t=RealtimeScreenTouch(('localhost',1111),key,q)
				s=stfServices(('localhost',1100),key,q2)
				self.clients[key]={'touch':t,'cap':c,'touchQ':q,'services':s,'servicesQ':q2}
				print (self.keys(),'keys')
				return 1
			except Exception as e:
				print (str(e))
				return 0
	def closeAll(self,key):
		r=self.clients.get(key)
		if r:
			c=r.get('cap')
			if c:
				# c.close()
				print ('cap',c.close())
			t=r.get('touch')
			if t:
				# t.close()
				print ('touch',t.close())
			s=r.get('services')
			if s:
				print ('services',s.close())
			self.clients.pop(key)	
			del r
			return 1
		else:
			return 0
	def sendTouch(self,key,action,seq):
		# print (seq)
		r=self.clients.get(key)
		if r:
			q=r.get('touchQ')
			if q:
				q.put(action.encode('ascii'))
				return 1
			else:
				return 0
		else:
			return 0
	def sendkeyevent(self,key,type_t,data):
		r=self.clients.get(key)
		if r:
			q2=r.get('servicesQ')
			if q2:
				q2.put([type_t,data])
				return 1
			else:
				return 0
		else:
			return 0
	def sendTouch2(self,key,action,seq):
		print (seq)
		r=self.clients.get(key)
		if r:
			t=r.get('touch')
			if t:
				t.sendF(action.encode('ascii'))
				return 1
			else:
				return 0
		else:
			return 0
	def startCap(self,key):
		r=self.clients.get(key)
		if r:
			t=r.get('cap')
			if t:
				res=t.start()
				print ('cap start')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found'%key)
			return 0
	def startTouch(self,key):
		r=self.clients.get(key)
		if r:
			t=r.get('touch')
			if t:
				res=t.start()
				print (res,'touch start')
				return res
			else:
				print ('%s[touch] client not found'%key)
				return 0
		else:
			print ('%s not found')
			return 0
	def startServices(self,key):
		r=self.clients.get(key)
		if r:
			t=r.get('services')
			if t:
				res=t.start()
				print (res,'stfServices start')
				return res
			else:
				print ('%s[stfServices] client not found'%key)
				return 0
		else:
			print ('%s not found')
			return 0