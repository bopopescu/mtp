import socket,sys,random
import time
from .. import socketio
import struct,sys
from .adbkit import *
from eventlet.queue import Queue
import eventlet
eventlet.monkey_patch()
from .wire_pb2 import *
from .messagestream import delimitedStream,delimitingStream
from .keyMap import keyMap

class ServiceError(Exception):
	def __init__(self,name='',location=''):
		Exception.__init__(self)
		self.name = name
		self.location=location
	def __str__(self):
		return repr("%s in <%s>"%(self.name,self.location))

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

class Service():
	def __init__(self,serial,ports):
		self.serial=serial
		self.ports=ports
		self.init_resource()
	def init_resource(self):
		self.service_resource = {
			'requiredVersion': '1.0.2',
			'pkg': 'jp.co.cyberagent.stf',
			'main': 'jp.co.cyberagent.stf.Agent',
			'apk': 'app/vendor/STFService/STFService.apk',
			'startIntent': {
				'action': 'jp.co.cyberagent.stf.ACTION_START',
				'component': 'jp.co.cyberagent.stf/.Service'
			}
	    }
	def forward_service(self,localport):
		print ('serviceport:%s'%localport)
		forward_tcp(self.serial,localport,1100)
	def forward_agent(self,localport):
		print('agentport:%s'%localport)
		forward_tcp(self.serial,localport,1090)
	def killProc(self,serial,commn):
		res=kill(serial,commn)
		print ('kill:',res)
	def killPid(self,pid):
		res=killPid(self.serial,pid)
	def install_service_apk(self):
		install(self.serial,self.service_resource['apk'])
	def installAll(self):
		self.killProc(self.serial,'stf.agent')
		apkpath=get_apk_path(self.serial,self.service_resource['pkg'])
		print ('apkpath',apkpath)
		if not apkpath:
			print ('will be install services pkg')
			self.install_service_apk()
		version=check_services_Version(self.serial,apkpath,self.service_resource['main'])
		if version==self.service_resource['requiredVersion']:
			print ('checkversion pass')
			self.callService()
			print (self.ports,'ports')
			self.forward_service(str(self.ports[0]))
			self.openAgent(apkpath)
			self.forward_agent(str(self.ports[1]))
		else:
			print ('checkversion fail')

	def callService(self):
		res=exe_shell(self.serial,"am startservice --user 0 -a '%s' -n '%s'"%(self.service_resource['startIntent']['action'],self.service_resource['startIntent']['component']))
	def openAgent(self,apkpath):
		res=exe_shell(self.serial,"export CLASSPATH='%s'\; \exec app_process /system/bin '%s'"%(apkpath,self.service_resource['main']))

class stfServices():
	def __init__(self,addr,serial):
		self.serial=serial
		self.addr=addr
		# self.desiredState=StateQueue()
		self.serviceQueue=Queue(500)
		self.send_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
		self.get_status=0 #0:初始化;1:接收状态;-1:关闭状态;-2:关闭ing
		self.service=Service(serial,[self.addr[1],self.addr[1]+1])
		self.msgQ={}
		self.phone=None
	def log(self,log):
		print ('[%s-stfService]:%s'%(self.serial,log))
	def createSocket(self):
		try:
			self.log('addr:%s_%s'%(self.addr[0],self.addr[1]))
			self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket22=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.socket.settimeout(0.5)
			self.socket.connect(self.addr)
			time.sleep(1)
			self.socket22.connect((self.addr[0],self.addr[1]+1))
			return 1
		except Exception as e:
			self.errorhandler('connectError_'+str(e))
			return 0
	def install(self):
		self.log('installing stfservice resource')
		self.service.installAll()
	def init(self):
		self.install()	
	def errorhandler(self,error=''):
		self.close()
		data={'status':1,'msg':error}
		socketio.emit('errormsg%s'%self.serial,data,namespace='/touch')
		print (data,'error')
	def responseHandler(self,data):
		if not data:
			return
		data=delimitedStream(data)
		envelop=Envelope()
		envelop.ParseFromString(data)
		print (envelop.type,envelop.id,'responseHandler')		
	def eventHandler(self,data):
		data=delimitedStream(data)
		envelop=Envelope()
		envelop.ParseFromString(data)
		if envelop.id:
			self.msgQ[str(envelop.id)]=envelop
		else:
			etype=envelop.type
			if etype==EVENT_BATTERY:
				temp=BatteryEvent()
				temp.ParseFromString(envelop.message)
				print ('BatteryEvent',temp.status,temp.health,temp.level,type(temp))
			elif etype==EVENT_AIRPLANE_MODE:
				temp=AirplaneModeEvent()
				temp.ParseFromString(envelop.message)
				print ('AirplaneModeEvent',temp.enabled)
			elif etype==EVENT_BROWSER_PACKAGE:
				temp=BrowserPackageEvent()
				temp.ParseFromString(envelop.message)
				print ('BrowserPackageEvent',temp.selected)
				for app in temp.apps:
					print ('app',app.name,app.component)
			elif etype==EVENT_CONNECTIVITY:
				temp=ConnectivityEvent()
				temp.ParseFromString(envelop.message)
				print ('ConnectivityEvent',temp.connected)
			elif etype==EVENT_PHONE_STATE:
				temp=PhoneStateEvent()
				temp.ParseFromString(envelop.message)
				print ('PhoneStateEvent',temp.state)
			elif etype==EVENT_ROTATION:
				temp=RotationEvent()
				temp.ParseFromString(envelop.message)
				print ('RotationEvent',temp.rotation)
				self.notify('RotationEvent',{'rotation':temp.rotation})
			else:
				print ('heheh',envelop.type)	
	def notify(self,eventname,data):
		socketio.emit('event',{'eventname':eventname,'data':data},namespace='/stfservice'+self.serial)
	def getInfo(self):
		buffersize=1024
		while self.get_status>0:
			try:
				data=self.socket.recv(buffersize)
				if data:
					self.eventHandler(data)
				else:
					# self.log('stfservice recv empty data')
					time.sleep(0.5)
			except socket.timeout:
				pass
			except Exception as e:
				self.errorhandler('getInfoError_%s'%str(e))
				break
		self.get_status=-1
		self.socket.close()
		self.log('[get close]')	
	def send(self):
		while self.send_status>0:
			try:
				data=self.serviceQueue.get(False)
				if data[0]=='agent':
					self.socket22.send(data[1])
				else:
					self.socket.send(data[1])
					# self.sendhandler(data)
			except eventlet.queue.Empty:
				time.sleep(0.01)
			except Exception as e:
				# print (str(e))
				self.errorhandler('sendError_%s'%str(e))
				break
		self.send_status=-1
		self.log('[send close]')
	def sendF(self,data):
		self.socket.send(data)
	def start(self):
		self.log('start')
		if self.send_status!=1 and self.get_status!=-2 and self.send_status!=1 and self.get_status!=-2:
			if self.createSocket():
				self.get_status=1
				self.send_status=1
				t1=eventlet.spawn_n(self.send)
				t2=eventlet.spawn_n(self.getInfo)
				self.log('stfservice start success')
				return 1
			else:
				self.log('stfservice start failed:connect error')
				return 0
		else:
			self.log('stfservice already started')
			return 0
	def close(self):
		if self.send_status==1 and self.get_status==1 :
			self.send_status=-2
			self.get_status=-2
			socketio.emit('event2','stop',namespace='/stfservice')
			print ('stfservice close success')
			return 1
		else:
			print ('stfservice close fail:already close')
			return 0
	def getkey(self,keyname):
		key=keyMap.get('KEYCODE_'+keyname.upper())
		if key:
			return key
		else:
			print('unKnown key:%s'%keyname)
			return None
	def runAgentCommand(self,type1,message):
		envelop=Envelope()
		envelop.type=type1
		envelop.message=message
		self.serviceQueue.put(['agent',delimitingStream(envelop.SerializeToString())])
	def runServiceCommand(self,mid,typeT,message):
		envelop=Envelope()
		envelop.type=typeT
		envelop.message=message
		envelop.id=mid
		self.serviceQueue.put(['service',delimitingStream(envelop.SerializeToString())])
		eventlet.spawn_n(self.getResponse,mid)
	def getProperties(self,data):
		d=GetPropertiesRequest()
		d.properties.extend([
            'imei', 'phoneNumber', 'iccid', 'network'
        ])
		mid=random.randint(10001,99999)
		self.runServiceCommand(mid,GET_PROPERTIES,d.SerializeToString())
	def GetBrowsersRequest(self,data):
		d=GetBrowsersRequest()
		mid=random.randint(10001,99999)
		self.runServiceCommand(mid,GET_PROPERTIES,d.SerializeToString())
	def setlockStatue(self,data):
		d=SetKeyguardStateRequest()
		if data['enabled']==True or data['enabled']=='true':
			d.enabled=True
		else:
			d.enabled=False
		mid=random.randint(10001,99999)
		self.runServiceCommand(mid,GET_PROPERTIES,d.SerializeToString())
	def getResponse(self,mid):
		for i in range(10):
			envelop=self.msgQ.get(str(mid))
			if envelop:
				self.msgQ.pop(str(mid))
				if envelop.type==GET_PROPERTIES:
					temp=GetPropertiesResponse()
					temp.ParseFromString(envelop.message)
					self.phone=temp.properties
					print (temp)
				elif envelop.type==GET_BROWSERS:
					temp=GetBrowsersResponse()
					temp.ParseFromString(envelop.message)
					print (temp,temp.selected)
				elif envelop.type==SET_KEYGUARD_STATE:
					temp=SetKeyguardStateResponse()
					temp.ParseFromString(envelop.message)
					print (temp)					
				else:
					print ('else')
					return
				return
			else:
				time.sleep(0.1)
		print ('nothing')

	def type(self,data):
		d=DoTypeRequest()
		d.text=data['text']
		self.runAgentCommand(DO_TYPE,d.SerializeToString())
	def keyDown(self,data):
		d=KeyEventRequest()
		d.event=DOWN
		key=self.getkey(data['key'])
		if key:
			d.keyCode=key	
			self.runAgentCommand(DO_KEYEVENT,d.SerializeToString())
	def keyUp(self,data):
		d=KeyEventRequest()
		d.event=UP
		key=self.getkey(data['key'])
		if key:
			d.keyCode=key	
			self.runAgentCommand(DO_KEYEVENT,d.SerializeToString())		
	def keyPress(self,data):
		d=KeyEventRequest()
		d.event=PRESS
		key=self.getkey(data['key'])
		if key:
			d.keyCode=key	
			self.runAgentCommand(DO_KEYEVENT,d.SerializeToString())
	def wake(self,data):
		d=DoWakeRequest()
		self.runAgentCommand(DO_WAKE,d.SerializeToString())
		print ('dowake')
	def rotate(self,data):
		d=SetRotationRequest()
		d.rotation=data['rotation']
		d.lock=data['lock']
		self.runAgentCommand(SET_ROTATION,d.SerializeToString())
