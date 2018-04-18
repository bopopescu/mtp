import socket
import time
# from .. import socketio
import struct,sys
# from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()
class sendInfo():
	def __init__(self,sq,ip='localhost',port=1111):
		self.sq=sq
		addr=(ip,port)
		self.sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sc.connect(addr)

	def getImgInfo(self):
		buffersize=1024
		while True:
			try:
				data=self.sc.recv(buffersize)
				print ('minitouch:',data)
			except Exception as e:
				print ('minitouchError',str(e))
				self.sc.close()
				break
	def send(self):
		while True:
			try:
				data=self.sq.get()
				print ('getdata',data)
				self.sc.send(data)
			except Exception as e:
				print (str(e))
				break
def init2(q,a):
	si=sendInfo(q)
	print ('fff',a)
	eventlet.spawn(si.getImgInfo)
	eventlet.spawn(si.send)