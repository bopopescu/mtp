import eventlet
eventlet.monkey_patch()
import socket,sys
import time
from  .. import socketio
from .adbkit import *
# from .adbkit import get_deviceInfo
import struct,sys
from eventlet.queue import Queue

class MyError(Exception):
	def __init__(self, name):
		Exception.__init__(self)
		self.name = name
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
				'src':'app/vendor/minicap/bin/%s/minicap%s'%(deviceInfos['abi'],deviceInfos['bin']),
				'dest':'/data/local/tmp/minicap',
				'comm':'minicap',
				'mode':'0755'
			},
			'lib':{
				'src':'app/vendor/minicap/shared/android-%s/%s/minicap.so'%(deviceInfos['sdk'],deviceInfos['abi']),
				'dest':'/data/local/tmp/minicap.so',
				'mode':'0755'
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
		self._killProc(self.serial,'minicap')
		src=self.minicap_resource
		if src.get('bin'):
			self._removeResource(src['bin'])
			self._installResource(src['bin'])
		if src.get('lib'):
			self._removeResource(src['lib'])
			self._installResource(src['lib'])	
	def killPid(self,pid):
		res=killPid(self.serial,pid)
	def forward_minicap(self):
		forward(self.serial,self.port,'minicap')
	def minicap_run(self,cmd):
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
		self.addr=addr
		self.serial=serial
		self.pid=-1
		self.desiredState=StateQueue()
		self.socket=None
		self.runningState=1 #0 STATE_STOPPED = 1 STATE_STARTING = 2 STATE_STARTED = 3 STATE_STOPPING = 4
		self.minicapService=MinicapService(serial,addr[1],deviceInfos)
		self.recv_status=0 #0:stoped;1:start;-2:stoping
		self.push_status=0 #0:stoped;1:start;-2:stoping
		self._recvData_init()
		self.socket=None
	def _recvData_init(self):
		self.__dataq=Queue(1000)
		self.readBannerBytes=0
		self.bannerLength=0
		self.readFrameBytes=0
		self.frameBodyLength=0
		self.frameBodyLengthStr=b''
		self.frameBody=b''
		self.banner={'version':0,'length':0,'pid':0,'realWidth':0,'realHeight':0,'virtualWidth':0,'realHeight':0,'orientation':0,'quirks':0}
	def recvdata(self):
		while self.recv_status>0:
			try:
				data=self.socket.recv(4096)
				if data:
					self.__dataq.put(data)
				else:
					assert False,'recv empty data'
			except socket.timeout:
				pass
			except Exception as e:
				s=sys.exc_info()
				self.errorhandler('recvdata','recvError_%s_%s'%(str(e),s[2].tb_lineno))
				break
		self.recv_status=0
		print ('[recvClose]')
	def createSocket(self):
		try:
			if self.socket:
				self.socket.close()
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(0.2)
			self.socket.connect(self.addr)
		except Exception as e:
			self.errorhandler('createSocket','Minicap connectError'+str(e))
			raise MyError('socket error')
	def processdata(self):
		while self.push_status>0:
			try:
				data=self.__dataq.get(timeout=0.2)
				self.myReadMsg(data)
			except eventlet.queue.Empty:
				time.sleep(0.05)
			except Exception as e:
				s=sys.exc_info()
				self.errorhandler('processdata','processdataError_%s_%s'%(str(e),str(s[2].tb_lineno)))
				break
		self.push_status=0
		print ('[processClose]')
	def myReadMsg(self,streamInfo):
		if self.bannerLength==0:
			self.banner['version'],self.banner['length'],self.banner['pid'],self.banner['realWidth'],self.banner['realHeight'],self.banner['virtualWidth'],self.banner['virtualHeight'],self.banner['orientation'],self.banner['quirks']=struct.unpack('<BBIIIIIBB',streamInfo[:24])
			self.pid=self.banner['pid']
			self.bannerLength=self.banner['length']
			print ('banner:',self.banner)
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
			socketio.emit('imgdata%s'%self.serial,data,namespace='/screen')
			# socketio.emit('imgdata',data,room=self.key,namespace='/screen')
		except Exception as e:
			print ('socketio error:%s'%str(e))	
	def log(self,log):
		print ('[%s-minicap] %s'%(self.serial,log))
	def errorhandler(self,funcname='',error=''):
		print ('[minicap Error in func<%s>]: %s'%(funcname,error))
	def _startService(self):
		self.log('Launching MiniCap service')
		try:
			# pid=checkPid(self.serial,'minicap')
			# self.log('pid:%s'%pid)
			cmd="-P %s"%self.frameConfig.toString()
			self.minicapService.minicap_run(cmd)
			self.log('execute cmd:%s'%cmd)
		except Exception as e:
			self.errorhandler('_startService',str(e))
			raise MyError('startService error')
	def _waitForPid(self):
		for i in range(10):
			if self.pid>0:
				self.log('get minicap pid%s'%self.pid)
				return self.pid
			time.sleep(0.1)
		if self.pid<=0:
			self.errorhandler('_waitForPid','cannot get pid')
			raise MyError('cannot get pid')
	def __connectService(self):
		self.log('Connecting to minicap service...')
		try:
			self.minicapService.forward_minicap()
			self.log('addr:%s'%self.addr[1])
			self.createSocket()
			if self.recv_status==0 and self.push_status==0:
				self.recv_status=1
				self.push_status=1
				t1=eventlet.spawn_n(self.recvdata)
				t2=eventlet.spawn_n(self.processdata)
			else:
				self.errorhandler('__connectService','recv status error:%s,%s'%(self.recv_status,self.push_status))
				raise MyError('__connectService','recv status error:%s,%s'%(self.recv_status,self.push_status))
				# self.log('Connecting to minicap service FAILED')
		except MyError as e:
			self.errorhandler('__connectService',e.name)
			# self.log('Connecting to minicap service FAILED')
			raise MyError(e.name)
		except Exception as e:
			self.errorhandler('__connectService',str(e))
			# self.log('Connecting to minicap service FAILED')
			raise MyError(str(e))
	def _disconnectService(self):
		self.log('Disconnecting from minicap service')
		if self.recv_status==1 and self.push_status==1:
			self.recv_status=-2
			self.push_status=-2
		else:
			self.log('Disconnecting from minicap service SKIP')
		if self.socket is not None:
			# self.socket.close()
			self.log('close socket')
	def _stopService(self):
		if self.pid>0:
			self.log('Stopping minicap service')
			self.minicapService.killPid(self.pid)
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
			self.errorhandler('_stop','recv:%s;push:%s'%(self.recv_status,self.push_status))
		self._stopService()
		self._recvData_init()
		self.pid=-1
		self.socket=None
		self.recv_status=0
		self.push_status=0
		self.log('Stopped minicap')
		self.runningState=1
	def _ensureState(self):
		if self.desiredState.isEmpty():
			return
		if self.runningState==2 or self.runningState==4:
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
					socketio.emit('system','start success',namespace='/screen')
				except Exception as e:
					self._stop()
				finally:
					self._ensureState()
			else:
				self.log('stop ignore')
		elif self.runningState==3:
			if self.desiredState.get()==1:
				self.runningState==4
				try:
					self._stop()
				finally:
					self._ensureState()
			else:
				self.log('start ignore')
				socketio.emit('system','start fail',namespace='/screen')
	def init(self):
		self.install()
		display=getDisplayInfo(self.serial)
		if display:
			real={'width':display['width'],'height':display['height']}
			virtual={'width':display['width'],'height':display['height'],'rotation':display['rotation']}
			self.frameConfig=FrameConfig(real,virtual)
			self.log('get display infos:%s'%display)
		else:
			self.frameConfig=None
			self.log('init failed cause displa is None')
	def install(self):
		self.log('installing minicap resource')
		self.minicapService.installAll()
	def start(self):
		self.log('Requesting frame producer to start')
		self.desiredState.push(3)
		self._ensureState()
	def stop(self):
		self.log('Requesting frame producer to stop')
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
