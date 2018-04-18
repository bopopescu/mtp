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
				'mode':'0755'
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
		self.killProc(self.serial,'minitouch')
		src=self.minitouch_resource
		if src.get('bin'):
			self.removeResource(src['bin'])
			self.installResource(src['bin'])
		if src.get('lib'):
			self.removeResource(src['lib'])
			self.installResource(src['lib'])
	def minitouch_run(self,cmd=''):
		res=exe_shell(self.serial,'exec %s%s'%(self.minitouch_resource['bin']['dest'],cmd))
		print ('minitouch res:%s'%res)

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
			return 1
		except Exception as e:
			self.errorhandler('connectError','createSocket')
			return 0
	def log(self,log):
		print ('[%s-minitouch] %s'%(self.serial,log))
	def errorhandler(self,error='',location=''):
		raise TouchError(error,location)
		print ('[minitouch] ERROR: %s'%error)
	def _startService(self):
		try:
			self.log('Launching minitouch service')
			t1=eventlet.spawn_n(self.minitouchService.minitouch_run)
		except Exception as e:
			self.errorhandler(str(e),'_startService')
			# raise TouchError('startService error')
	def __connectService(self):
		self.log('Connecting to minitouch service')
		try:
			self.minitouchService.forward_minitouch()
			self.log('addr:%s'%self.addr[1])
			self.createSocket()
			if self.get_status==0 and self.send_status==0:
				self.send_status=1
				self.get_status=1
				t1=eventlet.spawn_n(self.getInfo)
				t2=eventlet.spawn_n(self.send)
			else:
				self.errorhandler('get:%s/send:%s Error'%(self.get_status,self.send_status),'__connectService')
				self.log('Connecting to minitouch service FAILED')
		# except TouchError as e:
		# 	self.errorhandler(e.name)
		# 	self.log('Connecting to minitouch service FAILED')
		# 	raise MyError(e.name)
		except Exception as e:
			s=sys.exc_info()
			# self.errorhandler(str(e)+str(s[2].tb_lineno))
			self.errorhandler(str(e),'__connectService')
			self.log('Connecting to minitouch service FAILED')
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
			self.log('revb status2 error:%s_%s'%(self.get_status,self.send_status))
			self.send_status=-2
			self.get_status=-2
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
			time.sleep(0.1)
		if self.pid<=0:
			self.errorhandler('can not get pid','_waitForPid')
			# raise TouchError('pid not found')
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
					# print ('f1'*10)
					time.sleep(2)
					# print ('f1'*10)
					self.__connectService()
					self._waitForPid()
					self.runningState=3
					self.log('minitouch service started')
				# except TouchError as e:
				# 	self.log('EXCEPTION-->STOP:%s'%str(e.name))
				# 	self._stop()
				except Exception as e:
					s=sys.exc_info()
					self.log('EXCEPTION-->STOP:%s'%str(e))
					if self.runningState!=1:
						self._stop()
					else:
						self.log('exception SKIP, already Closed')
				finally:
					self._ensureState()
			else:
				self.log('stop SKIP')
		elif self.runningState==3:
			if self.desiredState.get()==1:
				self.runningState==4
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
	def getInfo(self):
		buffersize=1024
		self.log('<start get>')
		errorFlag=0
		while self.get_status>0:
			try:
				data=self.socket.recv(buffersize)
				if data:
					infos=data.decode('utf-8').split('\n')
					self.log(infos)
					self.version=infos[0].split(' ')[1]
					self.max_contacts=float(infos[1].split(' ')[1])
					self.max_x=int(infos[1].split(' ')[2])
					self.max_y=int(infos[1].split(' ')[3])
					self.max_pressure=int(infos[1].split(' ')[4])
					self.pid=int(infos[2].split(' ')[1])
					self.log('getinfos:%s_%s_%s_%s'%(self.version,self.pid,self.max_x,self.max_y))
				else:
					assert False,'touchService recv empty data'
			except socket.timeout:
				pass
			except Exception as e:
				errorFlag=1
				self.log('getInfoError_%s'%str(e))
				
				# self.sc.close()
				break
		# self.get_status=0
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
				self.log('sendError_%s'%str(e),'send')
				break
		self.log('[close send]')
		if errorFlag:
			self._stop()
	def gestureStart(self,seq):
		self.actionStatus=True
	def gestureStop(self,seq):
		self.actionStatus=False
	def touchDown(self,point):
		print (point,'point')
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

