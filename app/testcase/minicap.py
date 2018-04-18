import eventlet
eventlet.monkey_patch()
import socket,sys
import time
from  .. import socketio
from .adbkit import *
# from .adbkit import get_deviceInfo
import struct,sys
from eventlet.queue import Queue

class CapError(Exception):
	def __init__(self,name='',location=''):
		Exception.__init__(self)
		self.name = name
		self.location=location
	def __str__(self):
		return repr("%s in <%s>"%(self.name,self.location))

class FrameConfig():
	def __init__(self,real,virtual):
		self.realWidth = real['width']
		self.realHeight= real['height']
		self.virtualWidth=virtual['width']
		self.virtualHeight = virtual['height']
		self.rotation=virtual['rotation']
	def toString(self):
		return '%sx%s@%sx%s/%d'%(self.realWidth,self.realHeight,self.virtualWidth,self.virtualHeight,self.rotation)


class MinicapService():
	def __init__(self,serial,port,deviceInfos):
		self.serial=serial
		self.port=port
		self._init_resource(deviceInfos)

	def _init_resource(self,deviceInfos):
		self.minicap_resource={
			'bin':{
				'src':'/Users/xz/newMtp/mtp/vendor/minicap/bin/%s/minicap%s'%(deviceInfos['abi'],deviceInfos['bin']),
				'dest':'/data/local/tmp/minicap',
				'comm':'minicap',
				'mode':'' #0755 对应新版adb。。。待查
			},
			'lib':{
				'src':'/Users/xz/newMtp/mtp/vendor/minicap/shared/android-%s/%s/minicap.so'%(deviceInfos['sdk'],deviceInfos['abi']),
				'dest':'/data/local/tmp/minicap.so',
				'mode':''  #0755 对应新版adb。。。待查
			}
		}
	def _installResource(self,src):
		res=push(self.serial,src['src'],src['dest'],src['mode'])
		# print ('install:',res)
	def _removeResource(self,src):
		res=rm(self.serial,src['dest'])
		# print ('remove:',res)
	def _killProc(self,serial,commn):
		res=kill(serial,commn)
		# print ('kill:',res)
	def installAll(self):
		return
		self._killProc(self.serial,'minicap')
		src=self.minicap_resource
		if src.get('bin'):
			# self._removeResource(src['bin'])
			self._installResource(src['bin'])
		if src.get('lib'):
			# self._removeResource(src['lib'])
			self._installResource(src['lib'])	
	def killPid(self,pid):
		res=killPid(self.serial,pid)
	def forward_minicap(self):
		forward(self.serial,self.port,'minicap')
	def minicap_run(self,cmd):
		# self._killProc(self.serial,'minicap')
		res=exe_shell(self.serial, 'LD_LIBRARY_PATH=%s exec %s %s'%('/data/local/tmp/',self.minicap_resource['bin']['dest'],cmd))

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

class Minicap():
	def __init__(self,addr,serial,deviceInfos):
		# self.room=room
		self.addr=addr
		self.serial=serial
		self.pid=-1
		self.desiredState=StateQueue()
		self.socket=None
		self.runningState=1 #0 STATE_STOPPED = 1 STATE_STARTING = 2 STATE_STARTED = 3 STATE_STOPPING = 4
		self.recv_status=0 #0:stoped;1:start;-2:stoping
		self.push_status=0 #0:stoped;1:start;-2:stoping
		self._recvData_init()
		self.socket=None
		self.minicapService=MinicapService(serial,addr[1],deviceInfos)
		self.namespace='/screen%s'%self.serial
	def _recvData_init(self):
		self.__dataq=Queue(1000)
		self.readBannerBytes=0
		self.bannerLength=0
		self.readFrameBytes=0
		self.frameBodyLength=0
		self.frameBodyLengthStr=b''
		self.frameBody=b''
		self.banner={'version':0,'length':0,'pid':0,'realWidth':0,'realHeight':0,'virtualWidth':0,'realHeight':0,'orientation':0,'quirks':0}
	def errorhandler(self,error=''):
		print ('[%s-minicap] ERROR: %s'%(self.serial,error))
		# print ('[minicap Error]: %s'%(error))
		try:
			socketio.emit('system',{'name':'screenStatus','data':error},namespace=self.namespace)
		except:
			self.log('socketio send error')
	def createSocket(self):
		try:
			if self.socket:
				self.socket.close()
				self.socket=None
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(0.15)
			self.socket.connect(self.addr)
		except Exception as e:
			raise CapError('connect error:'+str(e),'createSocket')
	def recvdata(self):
		errorFlag=0
		while self.recv_status>0:
			try:
				data=self.socket.recv(4096)
				if data:
					self.__dataq.put(data)
				else:
					raise CapError('recv empty data','recvdata')
			except socket.timeout:
				pass
			except Exception as e:
				s=sys.exc_info()
				# self.log('recvError_%s_%s'%(str(e),s[2].tb_lineno))
				self.errorhandler('recvError_%s_%s'%(str(e),s[2].tb_lineno))
				errorFlag=1
				break
		self.recv_status=0
		self.log('[recvClose]')
		if errorFlag:
			self.runningState=4
			self._stop()
	def processdata(self):
		errorFlag=0
		while self.push_status>0:
			try:
				data=self.__dataq.get(timeout=0.1)
				self.ReadMsg(data)
			except eventlet.queue.Empty:
				time.sleep(0.05)
			except Exception as e:
				s=sys.exc_info()
				self.errorhandler('processdataError_%s_%s'%(str(e),str(s[2].tb_lineno)))
				# socketio.emit('system',str(e),namespace=self.namespace)
				errorFlag=1
				break
		self.push_status=0
		self.log('[processClose]')
		if errorFlag:
			self.runningState=4
			self._stop()
	def ReadMsg(self,streamInfo):
		if self.bannerLength==0:
			self.banner['version'],self.banner['length'],self.banner['pid'],self.banner['realWidth'],self.banner['realHeight'],self.banner['virtualWidth'],self.banner['virtualHeight'],self.banner['orientation'],self.banner['quirks']=struct.unpack('<BBIIIIIBB',streamInfo[:24])
			self.pid=self.banner['pid']
			self.bannerLength=self.banner['length']
			self.getOneImageInfo(streamInfo[24:])
		else:
			self.getOneImageInfo(streamInfo)
	def getOneImageInfo(self,stream):
		for i,v in enumerate(stream):
			if self.readFrameBytes<4:
				self.frameBodyLengthStr+=stream[i:i+1]
				if self.readFrameBytes==3:
					self.frameBodyLength,=struct.unpack('<I',self.frameBodyLengthStr)
				self.readFrameBytes+=1
			else:
				if len(stream)-i>=self.frameBodyLength:
					self.frameBody+=bytes(stream[i:i+self.frameBodyLength])
					self.datahandler(self.frameBody)
					temp=self.frameBodyLength
					self.frameBody=b''
					self.readFrameBytes,self.frameBodyLength=0,0
					self.frameBodyLengthStr=b''
					if i+temp<len(stream):
						# print ('<<<',len(stream)-i-temp)
						self.getOneImageInfo(stream[i+temp:])
						break
					else:
						break
				else:
					self.frameBody+=bytes(stream[i:len(stream)])
					self.readFrameBytes+=len(stream)-i
					self.frameBodyLength-=len(stream)-i
					break
	def datahandler(self,data):
		try:
			# socketio.emit('imgdata%s'%self.serial,data,namespace='/screen')
			# socketio.emit('imgdata',data,room=self.room,namespace='/screen')
			socketio.emit('imgdata',data,namespace=self.namespace)
		except Exception as e:
			print ('socketio error:%s'%str(e))	
	def log(self,log):
		print ('[%s-minicap] %s'%(self.serial,log))

	def _startService(self):
		try:
			self.log('Launching MiniCap service')
			cmd="-P %s"%self.frameConfig.toString()
			self.minicapService.minicap_run(cmd)
			time.sleep(0.8)
		except Exception as e:
			raise CapError('startService error:'+str(e),'_startService')
	def _waitForPid(self):
		self.log('waiting pid...')
		for i in range(10):
			if self.pid>0:
				self.log('get minicap pid%s'%self.pid)
				return self.pid
			time.sleep(0.1)
		if self.pid<=0:
			raise CapError('cannot get pid','_waitForPid')
	def __connectService(self):
		try:
			self.log('Connecting to minicap service...')
			self.minicapService.forward_minicap()
			self.log('addr:%s'%self.addr[1])
			self.createSocket()
			if self.recv_status==0 and self.push_status==0:
				self.recv_status=1
				self.push_status=1
				t1=eventlet.spawn_n(self.recvdata)
				t2=eventlet.spawn_n(self.processdata)
			else:
				raise CapError('recv:%s/push:%s Error'%(self.recv_status,self.push_status),'__connectService')
		except Exception as e:
			raise CapError(str(e),'__connectService')
	def _disconnectService(self):
		self.log('Disconnecting from minicap service')
		if self.recv_status==1:
			self.recv_status=-2
		if self.push_status==1:
			self.push_status=-2
		if self.socket is not None:
			# self.socket.close()
			self.log('close socket')
	def _stopService(self):
		if self.pid>0:
			st=time.time()
			self.log('Stopping minicap service')
			self.minicapService.killPid(self.pid)
			print ('kill time',time.time()-st)
			# assert False,'ffff'
			# time.sleep(10)
		else:
			self.log('Stopping minicap service SKIP')
	def checkclosed(self):
		for i in range(30):
			if self.recv_status==0 and self.push_status==0:
				return 0
			time.sleep(0.01)
		return 1
	def _stop(self):
		self._disconnectService()
		if self.checkclosed():
			self.log('WARNING_recv:%s;push:%s'%(self.recv_status,self.push_status))
		self._stopService()
		self._recvData_init()
		self.pid=-1
		self.socket=None
		self.recv_status=0
		self.push_status=0
		self.runningState=1
		socketio.emit('system',{'name':'screenStatus','data':'disconnected'},namespace=self.namespace)
		self.log('Stopped minicap')
	def _ensureState(self):
		if self.desiredState.isEmpty():
			return
		if self.runningState==2 or self.runningState==4:
			self.log('WAIT')
			return 
		elif self.runningState==1:
			if self.desiredState.get()==3:
				try:
					self.runningState=2
					self._startService()
					self.__connectService()
					self._waitForPid()
					self.runningState=3
					self.log('Started minicap')
					socketio.emit('system',{'name':'screenStatus','data':'connected'},namespace=self.namespace)
				except Exception as e:
					self.errorhandler('EXCEPTION-->STOP:%s'%str(e))
					self.log('catch error,will close')
					if self.runningState!=1:
						self.runningState=4
						self._stop()
					else:
						self.log('ERROR SKIP, already Closed')
				finally:
					self._ensureState()
			else:
				self.log('stop ignore')
		elif self.runningState==3:
			if self.desiredState.get()==1:
				try:
					self.runningState=4
					self._stop()
				finally:
					self._ensureState()
			else:
				self.log('start ignore'+str(self.runningState))
				# socketio.emit('system','start fail',self.namespace)
	def init(self):
		self.install()
		display=getDisplayInfo(self.serial)
		if display:
			real={'width':display['width'],'height':display['height']}
			virtual={'width':display['width'],'height':display['height'],'rotation':display['rotation']}
			self.frameConfig=FrameConfig(real,virtual)
			self.log('get display infos:%s'%display)
			return display
		else:
			self.frameConfig=None
			self.log('init failed cause display is None')
			return None
	def install(self):
		self.log('installing minicap resource')
		self.minicapService.installAll()
	def start(self):
		st=time.time()
		self.log('Requesting frame producer to start')
		self.desiredState.push(3)
		self._ensureState()
		print ('start time',time.time()-st)
	def stop(self):
		st=time.time()
		self.log('Requesting frame producer to stop')
		self.desiredState.push(1)
		self._ensureState()
		print ('stop time',time.time()-st)
	def restart(self):
		st=time.time()
		self.log('restart')
		self.stop()
		self.start()
		# if self.runningState==2 or self.runningState==3:
		# 	self.desiredState.push(1)
		# 	self.desiredState.push(3)
		# 	self._ensureState()
		# else:
			# self.log('restart error:%s'%(self.runningState))
		print ('total time',time.time()-st)
	def updateConfig(self,width,height):
		if self.frameConfig.virtualWidth==width and self.frameConfig.virtualHeight==height:
			self.log('Keeping %dx%d as current frame producer projection'%(width,height))
			return
		else:
			self.log('Setting frame producer projection to %dx%d'%(width,height))
			self.frameConfig.virtualWidth=width
			self.frameConfig.virtualHeight=height
			self.restart() #restart
	def updateRotation(self,rotation):
		if self.frameConfig.rotation==rotation:
			self.log('Keeping %d as current frame producer rotation'%rotation)
			return
		else:
			self.log('Setting frame producer rotation to %d'%rotation)
			self.frameConfig.rotation=rotation
			self.restart() #restart
