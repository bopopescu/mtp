import socket,sys
import time
from .. import socketio
from .ConnectDevice import ConnectScreenCap
from .adbkit import get_deviceInfo
import struct,sys
from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()
 

class RealtimeScreenCap():
	def __init__(self,addr,key):
		self.key=key
		self.addr=addr
		self.recv_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
		self.push_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
		self.recvData_init()
	def recvData_init(self):
		self.__dataq=Queue(1000)
		self.readBannerBytes=0
		self.bannerLength=0
		self.readFrameBytes=0
		self.frameBodyLength=0
		self.frameBodyLengthStr=b''
		self.frameBody=b''
		self.banner={'version':0,'length':0,'pid':0,'realWidth':0,'realHeight':0,'virtualWidth':0,'realHeight':0,'orientation':0,'quirks':0}
	# def init_minicap(self):
	# 	deviceInfos=get_deviceInfo(self.key)
	# 	c=ConnectScreenCap(self.key,deviceInfos)
	# 	c.connect_cap(self.addr[1])
	def connect(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(2)
			self.socket.connect(self.addr)
			return 1
		except Exception as e:
			self.errorhandler('connectError')
			return 0
	# def init(self):
	# 	t1=eventlet.spawn_n(self.init_minicap)
	def recvdata(self):
		while self.recv_status>0:
			try:
				data=self.socket.recv(4096)
				if data:
					self.__dataq.put(data)
				else:
					pass
					# print ('recv empty data')
					assert False,'recv empty data'
			except socket.timeout:
				pass
				# print ('timeout')
			except Exception as e:
				s=sys.exc_info()
				self.errorhandler('recvError_%s_%s'%(str(e),s[2].tb_lineno))
				break
		self.recv_status=-1
		self.socket.close()
		print ('[recvClose]')
	def myReadMsg(self,streamInfo):
		if self.bannerLength==0:
			self.banner['version'],self.banner['length'],self.banner['pid'],self.banner['realWidth'],self.banner['realHeight'],self.banner['virtualWidth'],self.banner['virtualHeight'],self.banner['orientation'],self.banner['quirks']=struct.unpack('<BBIIIIIBB',streamInfo[:24])
			self.bannerLength=self.banner['length']
			print ('banner:',self.banner)
			self.getOneImageInfo(streamInfo[24:])
		else:
			self.getOneImageInfo(streamInfo)
	def getOneImageInfo(self,stream):
		# try:
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
		# except Exception as e:
		# 	s=sys.exc_info()
		# 	print ('except',str(e),str(s[2].tb_lineno))
		# 	assert 1==2,'errorfuck'
	def datahandler(self,data):
		try:
			socketio.emit('imgdata%s'%self.key,data,namespace='/screen')
			# socketio.emit('imgdata',data,room=self.key,namespace='/screen')
		except Exception as e:
			print ('socketio error:%s'%str(e))
	def errorhandler(self,error=''):
		self.close()
		data={'status':1,'msg':error}
		socketio.emit('errormsg%s'%self.key,data,namespace='/screen')
		# socketio.emit('errormsg',data,room=self.key,namespace='/screen')
		print (data,'error')
	def processdata(self):
		while self.push_status>0:
			try:
				# print ('process')
				data=self.__dataq.get(timeout=2)
				self.myReadMsg(data)
				# time.sleep(0.5)
			except eventlet.queue.Empty:
				pass
				# print ('empty')
			except Exception as e:
				s=sys.exc_info()
				self.errorhandler('processdataError_%s_%s'%(str(e),str(s[2].tb_lineno)))
				# print ('except',str(e),str(s[2].tb_lineno))
				break
		self.push_status=-1

		print ('[processClose]')

	def close(self):
		if self.recv_status==1 and self.push_status==1:
			self.recv_status=-2
			self.push_status=-2
			# self.socket.close()
			socketio.emit('event','stop',namespace='/screen')
			# socketio.emit('event','stop',room=self.key,namespace='/screen')
			print ('cap close success')
			return 1
		else:
			print ('cap close fail:already close')
			return 0
	def start(self):
		if self.recv_status!=1 and self.recv_status!=-2 and self.push_status!=1 and self.push_status!=-2:
			if self.connect():
				self.recv_status=1
				self.push_status=1
				t1=eventlet.spawn_n(self.recvdata)
				t2=eventlet.spawn_n(self.processdata)
				print ('cap start sucess')
				return 1
			else:
				print ('cap start fail:connect error')
				return 0				
		else:
			print ('cap start fail:already starting')
			return 0
class RealtimeScreenTouch():
	def __init__(self,addr,key,queue):
		self.key=key
		self.addr=addr
		self.touchQueue=queue
		self.send_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
		self.get_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
	# def init_minitouch(self):		
	# 	deviceInfos=get_deviceInfo(self.key)
	# 	c=ConnectScreenCap(self.key,deviceInfos)
	# 	c.connect_touch(self.addr[1])
	# def init(self):
	# 	t1=eventlet.spawn_n(self.init_minitouch)
	def connect(self):
		try:
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(2)
			self.socket.connect(self.addr)
			return 1
		except Exception as e:
			self.errorhandler('connectError')
			return 0
	def errorhandler(self,error=''):
		self.close()
		data={'status':1,'msg':error}
		socketio.emit('errormsg%s'%self.key,data,namespace='/touch')
		# socketio.emit('errormsg',data,room=self.key,namespace='/touch')
		print (data,'error')
	def getInfo(self):
		buffersize=1024
		while self.get_status>0:
			try:
				data=self.socket.recv(buffersize)
				if data:
					print ('minitouch:',data)
				else:
					# pass
					assert False,'touchService recv empty data'
				# self.get_status=-3
				# break
			except socket.timeout:
				pass
			except Exception as e:
				# print ('minitouchError',str(e))
				self.errorhandler('getInfoError_%s'%str(e))
				# self.sc.close()
				break
		self.get_status=-1
		self.socket.close()
		print ('[get close]')
	def send(self):
		while self.send_status>0:
			try:
				data=self.touchQueue.get(False)
				# print ('getdata',data)
				# print (self.touchQueue.qsize(),'size')
				self.socket.send(data)
			except eventlet.queue.Empty:
				time.sleep(0.01)
			except Exception as e:
				# print (str(e))
				self.errorhandler('sendError_%s'%str(e))
				break
		self.send_status=-1
		print ('[send close]')
	def sendF(self,data):
		self.socket.send(data)
	def start(self):
		if self.send_status!=1 and self.get_status!=-2 and self.send_status!=1 and self.get_status!=-2:
			if self.connect():
				self.get_status=1
				self.send_status=1
				t1=eventlet.spawn_n(self.send)
				t2=eventlet.spawn_n(self.getInfo)
				print ('touch start success')
				return 1
			else:
				print ('touch start failed:connect error')
				return 0
		else:
			print ('touch already started')
			return 0
	def close(self):
		if self.send_status==1 and self.get_status==1:
			self.send_status=-2
			self.get_status=-2
			# self.socket.close()
			socketio.emit('event','stop',namespace='/touch')
			# socketio.emit('event','stop',room=self.key,namespace='/touch')
			print ('touch close success')
			return 1
		else:
			print ('touch close fail:already close')
			return 0


