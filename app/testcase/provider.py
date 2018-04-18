import requests,time,json
import logging
from .adbkit import get_devices
from .. import socketio
# import threading
from . import db
# from eventlet import time

class Provider():
	def __init__(self,m):
		print ('getone')
		self.initlogging()
		self.default_check_count=0
		self.temp=[]
		self.m=m
	def initlogging(self):
		self.logger = logging.getLogger('mylogger')
		self.logger.setLevel(logging.DEBUG)
		fh = logging.FileHandler('provider.log')
		fh.setLevel(logging.DEBUG)
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		self.logger.addHandler(fh)
		self.logger.addHandler(ch)
	def loop(self):
		while True:
			st=time.time()
			d=get_devices()
			if d is None:
				self.logger.error('error adbkit')
				continue
			current_all_devices=list(d.keys())
			if self.temp!=current_all_devices:
				print (self.temp,current_all_devices)
				new_devices=list(set(current_all_devices).difference(set(self.temp)))
				remove_devices=list(set(self.temp).difference(set(current_all_devices)))
				print (self.temp,current_all_devices,new_devices,remove_devices)
				if new_devices:
					self.add_devices(new_devices)
					# print ('add',self.temp,current_all_devices,new_devices)
				if remove_devices:
					self.remove_devices(remove_devices)
				# eventlet.spawn(self.add_devices(),new_devices)
				# eventlet.spawn(self.remove_devices(),remove_devices)
				# t=threading.Thread(target=self.device_update,args=(new_devices,remove_devices))
				# t.setDaemon(True)
				# t.start()
				self.temp=current_all_devices
				print (self.temp,current_all_devices,'fff')
			# elif self.default_check_count>3000:
			# 	t=threading.Thread(target=self.device_default_check,args=(current_all_devices,))
			# 	t.setDaemon(True)
			# 	t.start()
			# 	self.default_check_count=0
			time.sleep(0.5)
			self.default_check_count+=1
	def add_devices(self,devices):
		print ('ADD',devices)
		db.addDevices(devices)
		for serial in devices:
			ports=self.m.init(serial)
		socketio.emit('change','hehe',namespace='/default')
	def remove_devices(self,devices):
		print ('REMOVE',devices)
		st=time.time()
		db.removeDevices(devices)
		socketio.emit('change','hehe',namespace='/default')
		print (time.time()-st,'remove')
	# def device_update(self,new_devices,remove_devices):
	# 	print (new_devices,remove_devices,'update')
	# 	if new_devices:
	# 		# print ('new!!!',new_devices)
	# 		try:
	# 			r=requests.post('http://10.1.58.68:7777/testcase/adddevices',data={'infos':json.dumps(new_devices)},timeout=(0.5,8.5))
	# 			print (new_devices,'new')
	# 		except Exception as e:
	# 			self.temp=[]
	# 			print ('add error:%s'%str(e))
	# 	if remove_devices:
	# 		try:
	# 			r=requests.post('http://10.1.58.68:7777/testcase/removedevices',data={'infos':json.dumps(remove_devices)},timeout=(0.5,1.5))
	# 			print (remove_devices,'remove')
	# 		except:
	# 			self.temp=[]
	# 			print ('remove error')
	# 		# print (remove_devices,'remove')
	# 	# time.sleep(3)
	# def device_default_check(self,all_devices):
	# 	print (all_devices,'defaultCheck')
	# 	try:
	# 		r=requests.post('http://10.1.58.68:7777/testcase/devicecheck',data={'infos':json.dumps(all_devices)},timeout=(0.5,3.5))
	# 	except Exception as e:
	# 		print ('default_check_error',str(e))
			# self.temp=[]
		# time.sleep(3)
		# print (all_devices)
# p=Provider()
# p.loop()
