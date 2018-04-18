import socket
import time
# from .. import socketio
import struct,sys
# from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()
import wire_pb2
from messagestream import delimitedStream,delimitingStream
# print (dir(wire_pb2))
# print (wire_pb2.TEXT)



d=wire_pb2.DoTypeRequest()
d.text='3'
message=d.SerializeToString()
env1=wire_pb2.Envelope()
env1.type=wire_pb2.DO_TYPE
env1.message=message
ss=env1.SerializeToString()


p=wire_pb2.KeyEventRequest()
p.event=wire_pb2.PRESS
p.keyCode=100
message2=p.SerializeToString()
env2=wire_pb2.Envelope()
env2.type=wire_pb2.DO_KEYEVENT
env2.message=message2
ss2=env2.SerializeToString()



k=wire_pb2.SetWakeLockRequest()
k.enabled=1
env=wire_pb2.Envelope()
env.type=wire_pb2.SET_WAKE_LOCK
env.message=k.SerializeToString()
s2=env.SerializeToString()
# print ('s2',s2,len(s2))
# s3=struct.pack('<B8s',8,s2)
# fff=b"\x10\x0e\x1a'\n\x04full\x12\x04good\x1a\x03usb d(d1\x00\x00\x00\x00\x00\x80A@9\x06\x81\x95C\x8bl\x11@"
envelop=wire_pb2.Envelope()
envelop.ParseFromString(s2)
print (envelop.type,'ttt')
# envelop2.ParseFromString(s2)
# print (envelop2.type)
# ParseFromString
import struct
class service():
	def __init__(self,ip='localhost',port=1100):
		# self.sq=sq
		addr=(ip,port)
		self.sc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sc2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sc.connect(addr)
		self.sc2.connect(('localhost',1090))
		# self.ss=b''
	def getImgInfo(self):
		buffersize=4096
		while True:
			try:
				data=self.sc.recv(buffersize)
				if data:
					data=delimitedStream(data)
					envelop=wire_pb2.Envelope()
					envelop.ParseFromString(data)
					print (envelop.type,'type')
					# print (data,'data')
				else:
					# print ('fuck')
					continue
					# print ()
			except Exception as e:
				print ('agentError',str(e))
				self.sc.close()
				break
	def send(self):
		# print ('send')
		while True:
			try:
				# data=self.sq.get()
				# print ('getdata')
				# self.sc.send(s)
				s3=delimitingStream(s2)
				# self.sc.send(s3)
				# self.sc.send(s3)
				# self.sc.send(s3)
				time.sleep(2)
				print ('sent')
				self.sc2.send(delimitingStream(ss))
				# self.sc2.send(delimitingStream(ss))
				# self.sc2.send(delimitingStream(ss2))
				print ('senddata')
				break
			except Exception as e:
				print (str(e))
				break
def init2():
	si=service()
	print ('fff')
	t1=eventlet.spawn(si.getImgInfo)
	time.sleep(1)
	t2=eventlet.spawn(si.send)
	t1.wait()
	# time.sleep(10)
	# envelop2.ParseFromString(si.ss)
	# print (envelop2.id)
	# t1.join()
	# t2.join()
init2()
