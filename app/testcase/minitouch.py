import socket,sys
import time
from .. import socketio
from .adbkit import *
# from .adbkit import get_deviceInfo
# import struct
from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()

class TouchError(Exception):
	def __init__(self,name='',location=''):
		Exception.__init__(self)
		self.name = name
		self.location=location
	def __str__(self):
		return repr("%s in <%s>"%(self.name,self.location))

class MinitouchService():
	def __init__(self,serial,port,deviceInfos):
		self.serial=serial
		self.port=port
		self.init_resource(deviceInfos)
	def init_resource(self,deviceInfos):
		self.minitouch_resource={
			'bin':{
				'src':'app/vendor/minitouch/%s/minitouch%s'%(deviceInfos['abi'],deviceInfos['bin']),
				'dest': '/data/local/tmp/minitouch',
				'comm':'minitouch',
				'mode':'' #0755 对应新版adb。。。待查
			}
		}
	def forward_minitouch(self):
		forward(self.serial,self.port,'minitouch')
	def removeResource(self,src):
		res=rm(self.serial,src['dest'])
	def installResource(self,src):
		res=push(self.serial,src['src'],src['dest'],src['mode'])
	def killProc(self,serial,commn):
		res=kill(serial,commn)
	def killPid(self,pid):
		res=killPid(self.serial,pid)
	def installAll(self):
		return
		self.killProc(self.serial,'minitouch')
		src=self.minitouch_resource
		if src.get('bin'):
			# self.removeResource(src['bin'])
			self.installResource(src['bin'])
		if src.get('lib'):
			# self.removeResource(src['lib'])
			self.installResource(src['lib'])
	def minitouch_run(self,cmd=''):
		self.killProc(self.serial,'minitouch') #0907 add
		res=exe_shell(self.serial,'exec %s%s'%(self.minitouch_resource['bin']['dest'],cmd))

class StateQueue():
	def __init__(self):
		self.queue=[]
	def isEmpty(self):
		return len(self.queue)==0
	def push(self,data):
		found_flag=False
		for i,v in enumerate(self.queue):
			if v==data:
				self.queue=self.queue[:i+1]
				found_flag=True
				break
		if not found_flag:
			self.queue.append(data)
	def get(self):
		if not self.isEmpty():
			return self.queue.pop(0)
		else:
			return None

class Minitouch():
	def __init__(self,addr,serial,deviceInfos):
		self.serial=serial
		self.addr=addr
		self.pid=-1
		self.desiredState=StateQueue()
		self.socket=None
		self.runningState=1 #0 STATE_STOPPED = 1 STATE_STARTING = 2 STATE_STARTED = 3 STATE_STOPPING = 4
		self.minitouchService=MinitouchService(serial,self.addr[1],deviceInfos)
		self.touchQueue=Queue(500)
		self.send_status=0 #0:stoped;1:start;-2:stoping
		self.get_status=0 #0:stoped;1:start;-2:stoping
		self._init()
		self.actionStatus=None
		self.namespace='/screen%s'%self.serial
	def _init(self):
		self.version=-1
		self.max_contacts=-1
		self.max_x=-1
		self.max_y=-1
		self.max_pressure=-1
		self.pid=-1
	def createSocket(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(0.2)
			self.socket.connect(self.addr)
		except Exception as e:
			raise TouchError(str(e),'createSocket')
	def log(self,log):
		print ('[%s-minitouch] %s'%(self.serial,log))

	def errorhandler(self,error='',location=''):
		print ('[%s-minitouch] ERROR: %s'%(self.serial,error))
		try:
			socketio.emit('system',{'name':'touchStatus','data':error},namespace=self.namespace)
		except:
			self.log('socketio send error')
	def _startService(self):
		try:
			self.log('Launching minitouch service')
			t1=eventlet.spawn_n(self.minitouchService.minitouch_run)
		except Exception as e:
			raise TouchError(str(e),'_startService')
			# self.errorhandler(str(e),'_startService')

	def __connectService(self):
		try:
			self.log('Connecting to minitouch service')
			self.log('pid5:%s'%self.pid)
			self.minitouchService.forward_minitouch()
			self.log('pid3:%s'%self.pid)
			self.log('addr:%s'%self.addr[1])
			self.createSocket()
			self.log('pid4:%s'%self.pid)
			if self.get_status==0 and self.send_status==0:
				self.send_status=1
				t2=eventlet.spawn_n(self.send)
				self.get_status=1
				# time.sleep(2)
				t1=eventlet.spawn_n(self.getInfo)
			else:
				raise TouchError('get:%s/send:%s Error'%(self.get_status,self.send_status),'__connectService')
		except Exception as e:
			raise TouchError(str(e),'__connectService')
	def checkclosed(self):
		for i in range(30):
			if self.recv_status==0 and self.push_status==0:
				return 0
			time.sleep(0.01)
			print ('fuckcheck')
		return 1

	def install(self):
		self.log('installing minitouch resource')
		self.minitouchService.installAll()
	def init(self):
		self.install()		
	def _disconnectService(self):
		self.log('Disconnecting from minitouch service')
		if self.get_status==1 and self.send_status==1:
			self.send_status=-2
			self.get_status=-2
		else:
			self.log('WARNING revb status2 error:%s_%s'%(self.get_status,self.send_status))
		if self.socket:
			self.socket.close()
	def _stopService(self):
		if self.pid>0:
			self.log('Stopping minitouch service')
			self.minitouchService.killPid(self.pid)
		else:
			self.log('Stopping minitouch service SKIP')
	def _waitForPid(self):
		for i in range(10):
			if self.pid>0:
				self.log('get minitouch pid%s'%self.pid)
				return self.pid
			time.sleep(0.2)
		if self.pid<=0:
			raise TouchError('can not get pid','_waitForPid')
	def _stop(self):
		self._disconnectService()
		self._stopService()
		self.runningState=1

		self._init()
		self.pid=-1
		self.socket=None
		self.get_status=0
		self.send_status=0
		self.log('minitouch service stopped')
		socketio.emit('system',{'name':'touchStatus','data':'disconnected'},namespace=self.namespace)
	def _ensureState(self):
		if self.desiredState.isEmpty():
			return
		if self.runningState==2 or self.runningState==4:
			pass
		elif self.runningState==1:
			if self.desiredState.get()==3:
				try:
					self.runningState=2
					self._startService()
					time.sleep(1)
					self.__connectService()
					self.log('pid2:%s'%self.pid)
					self._waitForPid()
					self.runningState=3
					self.log('minitouch service started')
					socketio.emit('system',{'name':'touchStatus','data':'connected'},namespace=self.namespace)
				except Exception as e:
					self.errorhandler(str(e),'_ensureState')
					if self.runningState!=1:
						self.runningState=4
						self._stop()
					else:
						self.log('ERROR SKIP, already Closed')
				finally:
					self._ensureState()
			else:
				self.log('stop SKIP')
		elif self.runningState==3:
			if self.desiredState.get()==1:
				self.runningState=4
				try:
					self._stop()
				finally:
					self._ensureState()
			else:
				self.log('start SKIP')		
	def start(self):
		self.log('Requesting frame producer to START')
		self.desiredState.push(3)
		self._ensureState()
	def stop(self):
		self.log('Requesting frame producer to STOP')
		self.desiredState.push(1)
		self._ensureState()
	def restart(self):
		self.log('restart')
		if self.runningState==2 or self.runningState==3:
			self.desiredState.push(1)
			self.desiredState.push(3)
			self._ensureState()
		else:
			self.log('restart error:%s'%(self.runningState))
	def getInfo(self):
		buffersize=1024
		self.log('<start get>')
		errorFlag=0
		while self.get_status>0:
			try:
				data=b''
				for i in range(10):
					try:
						data+=self.socket.recv(buffersize)
					except:
						break
				if data:
					infos=data.decode('utf-8').split('\n')
					self.log(infos)
					self.version=infos[0].split(' ')[1]
					self.max_contacts=float(infos[1].split(' ')[1])
					self.max_x=int(infos[1].split(' ')[2])
					self.max_y=int(infos[1].split(' ')[3])
					self.max_pressure=int(infos[1].split(' ')[4])
					self.pid=int(infos[2].split(' ')[1])
					self.log('pid:%s'%self.pid)
					self.log('getinfos:%s_%s_%s_%s'%(self.version,self.pid,self.max_x,self.max_y))
				# else:
				# 	# pass
				# 	assert False,'touchService recv empty data'
			except socket.timeout:
				pass
			except Exception as e:
				errorFlag=1
				self.errorhandler('getInfoError_%s'%str(e))
				break
		self.get_status=0
		# if self.socket:
		# 	self.socket.close()
		self.log('<close get>')
		if errorFlag:
			self._stop()
	def send(self):
		self.log('[start send]')
		errorFlag=0
		while self.send_status>0:
			try:
				data=self.touchQueue.get(False)
				self.socket.send(data)
			except eventlet.queue.Empty:
				time.sleep(0.01)
			except Exception as e:
				errorFlag=1
				self.errorhandler('sendError_%s'%str(e))
				break
		self.send_status=0
		self.log('[close send]')
		if errorFlag:
			self._stop()
	def gestureStart(self,seq):
		self.actionStatus=True
	def gestureStop(self,seq):
		self.actionStatus=False
	def touchDown(self,point):
		socketData='d %s %s %s %s\n'%(point['contact'],round(point['x']*self.max_x),round(point['y']*self.max_y),round((point['pressure'] or 0.5)*self.max_pressure))
		if self.actionStatus:
			self.touchQueue.put(socketData.encode('ascii'))
	def touchMove(self,point):
		socketData='m %s %s %s %s\n'%(point['contact'],round(point['x']*self.max_x),round(point['y']*self.max_y),round((point['pressure'] or 0.5)*self.max_pressure))
		if self.actionStatus:
			self.touchQueue.put(socketData.encode('ascii'))
	def touchUp(self,point):
		socketData='u %s\n'%point['contact']
		if self.actionStatus:
			self.touchQueue.put(socketData.encode('ascii'))
	def touchCommit(self,data):
		if self.actionStatus:
			self.touchQueue.put('c\n'.encode('ascii'))
	def touchReset(self,data):
		if self.actionStatus:
			self.touchQueue.put('r\n'.encode('ascii'))

