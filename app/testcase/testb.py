
import socket
import time
from .. import socketio
# from threading import Thread
# from queue import Queue

import struct,sys
# from gevent.queue import Queue
# import gevent
# from gevent import monkey
# monkey.patch_socket()
from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()
q=Queue(1000)
# imgQ=Queue(1000)
class GetInfo():
	def __init__(self,q):
		# Thread.__init__(self)
		self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.socket.connect(('localhost',1313))
		self.q=q
		# self.imgQ=imgQ
	def run(self):
		while True:
			try:
				# print ('recv')
				data=self.socket.recv(4096)
				# print ('data:',data)
				self.q.put(data)
				# print (self.q.qsize())
			except Exception as e:
				print (str(e),'error')
				self.socket.close()
				break
class ProcessInfo():
	def __init__(self,q):
		# Thread.__init__(self)
		self.q=q
		self.readBannerBytes=0
		self.bannerLength=0
		self.readFrameBytes=0
		self.frameBodyLength=0
		self.frameBodyLengthStr=b''
		self.frameBody=b''
		self.banner={'version':0,'length':0,'pid':0,'realWidth':0,'realHeight':0,'virtualWidth':0,'realHeight':0,'orientation':0,'quirks':0}
	def myReadMsg(self,streamInfo):
		# print (len(streamInfo))
		if self.bannerLength==0:
			self.banner['version'],self.banner['length'],self.banner['pid'],self.banner['realWidth'],self.banner['realHeight'],self.banner['virtualWidth'],self.banner['virtualHeight'],self.banner['orientation'],self.banner['quirks']=struct.unpack('<BBIIIIIBB',streamInfo[:24])
			# self.banner['version']=struct.unpack('B',streamInfo[0])[0]
			# self.banner['length']=struct.unpack('B',streamInfo[1])[0]
			# self.banner['pid']=struct.unpack('I',bytes(streamInfo[2:6]))[0]
			# self.banner['realWidth']=struct.unpack('I',bytes(streamInfo[6:10]))[0]
			# self.banner['realHeight']=struct.unpack('I',bytes(streamInfo[10:14]))[0]
			# self.banner['virtualWidth']=struct.unpack('I',bytes(streamInfo[14:18]))[0]
			# self.banner['virtualHeight']=struct.unpack('I',bytes(streamInfo[18:22]))[0]
			# self.banner['orientation']=struct.unpack('B',streamInfo[22])[0]
			# self.banner['quirks']=struct.unpack('B',streamInfo[23])[0]
			self.bannerLength=self.banner['length']
			print ('banner:',self.banner)
			self.getOneImageInfo(streamInfo[24:])
		else:
			self.getOneImageInfo(streamInfo)

	def getOneImageInfo(self,stream):
		try:
			for i,v in enumerate(stream):
				if self.readFrameBytes<4:
					self.frameBodyLengthStr+=stream[i:i+1]
					if self.readFrameBytes==3:
						self.frameBodyLength,=struct.unpack('<I',self.frameBodyLengthStr)
						# print ('imgLen:',self.frameBodyLength)
					self.readFrameBytes+=1
				else:
					if len(stream)-i>=self.frameBodyLength:
						self.frameBody+=bytes(stream[i:i+self.frameBodyLength])
						self.send(self.frameBody)
						# print ('end',stream[i+self.frameBodyLength])
						self.frameBody=b''
						self.readFrameBytes=0
						self.frameBodyLength=0
						self.frameBodyLengthStr=b''
						# self.getOneImageInfo(stream[i+self.frameBodyLength:])
						return
					else:
						# print ('fill',len(stream),self.frameBodyLength)
						self.frameBody+=bytes(stream[i:len(stream)])
						self.readFrameBytes+=len(stream)-i
						self.frameBodyLength-=len(stream)-i
						break
		except Exception as e:
			s=sys.exc_info()
			print ('except',str(e),str(s[2].tb_lineno))
			print (len(self.frameBody),i,self.frameBodyLength,len(stream))


	def send(self,data):
		socketio.emit('hahaha',data)
	def run(self):
		while True:
			try:
				data=self.q.get()
				# print ('recv',len(data))
				self.myReadMsg(data)
				# time.sleep(0.5)
			except Exception as e:
				s=sys.exc_info()

				print ('except',str(e),str(s[2].tb_lineno))
				break
def init():
	print ('init*100')
	g=GetInfo(q)
	p=ProcessInfo(q)
# g.start()
# p.start()

	# t1=gevent.spawn(g.run)
	# t2=gevent.spawn(p.run)
	t1=eventlet.spawn(g.run)
	t2=eventlet.spawn(p.run)
	# t1.join()
	# t2.join()
# if __name__!='__name__':
# 	init()

