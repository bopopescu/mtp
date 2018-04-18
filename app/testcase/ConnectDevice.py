from .adbkit import rm,push,kill,getSize,exe_shell,forward,forward_tcp,check_services_Version,get_apk_path,install,exe_shell2,get_deviceInfo
import eventlet
eventlet.monkey_patch()
from . import db
from .. import socketio

class ConnectScreenCap():
	def __init__(self,serial):
		self.serial=serial
	def init_resource(self,deviceInfos):
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
		self.minitouch_resource={
			'bin':{
				'src':'app/vendor/minitouch/%s/minitouch%s'%(deviceInfos['abi'],deviceInfos['bin']),
				'dest': '/data/local/tmp/minitouch',
				'comm':'minitouch',
				'mode':'0755'
			}
		}

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
	def installResource(self,src):
		res=push(self.serial,src['src'],src['dest'],src['mode'])
		print ('install:',res)
	def removeResource(self,src):
		res=rm(self.serial,src['dest'])
		print ('remove:',res)
	def installAll(self,src):
		if src.get('bin'):
			self.removeResource(src['bin'])
			self.installResource(src['bin'])
		if src.get('lib'):
			self.removeResource(src['lib'])
			self.installResource(src['lib'])
	@staticmethod
	def killProc(serial,commn):
		res=kill(serial,commn)
		print ('kill:',res)
	def getsize(self):
		return getSize(self.serial)
	def minicap_connect(self):
		size=self.getsize()
		print ('size:',size)
		# cmd="-P %s@%s/1"%(size,size)
		cmd="-P 720x1280@356x632/90"
		res=exe_shell(self.serial, 'LD_LIBRARY_PATH=%s exec %s %s'%('/data/local/tmp/',self.minicap_resource['bin']['dest'],cmd))
	def minitouch_connect(self,cmd=''):
		res=exe_shell(self.serial,'exec %s%s'%(self.minitouch_resource['bin']['dest'],cmd))
		print ('excenddddddddddddddddddd')
	def forward_minicap(self,localport):
		forward(self.serial,localport,'minicap')
	def forward_minitouch(self,localport):
		forward(self.serial,localport,'minitouch')
	def forward_service(self,localport):
		forward_tcp(self.serial,localport,1100)
	def forward_agent(self,localport):
		forward_tcp(self.serial,localport,1090)
	def connect_cap(self,port):
		self.killProc(self.serial,'minicap')
		self.installAll(self.minicap_resource)
		self.minicap_connect()
		self.forward_minicap(port)
	def install_service_apk(self):
		install(self.serial,self.service_resource['apk'])
	def connect_touch(self,port):
		self.killProc(self.serial,'minitouch')
		self.installAll(self.minitouch_resource)
		self.minitouch_connect()
		self.forward_minitouch(port)
	def callService(self):
		res=exe_shell(self.serial,"am startservice --user 0 -a '%s' -n '%s'"%(self.service_resource['startIntent']['action'],self.service_resource['startIntent']['component']))
	def openAgent(self,apkpath):
		res=exe_shell(self.serial,"export CLASSPATH='%s'\; \exec app_process /system/bin '%s'"%(apkpath,self.service_resource['main']))
	def connect_service(self,ports):
		self.killProc(self.serial,'stf.agent')
		apkpath=get_apk_path(self.serial,self.service_resource['pkg'])
		if not apkpath:
			print ('will be install services pkg')
			self.install_service_apk()
		version=check_services_Version(self.serial,apkpath,self.service_resource['main'])
		if version==self.service_resource['requiredVersion']:
			print ('checkversion pass')
			self.callService()
			print (ports,'ports')
			self.forward_service(str(ports[0]))
			self.openAgent(apkpath)
			self.forward_agent(str(ports[1]))
		else:
			print ('checkversion fail')
	def _init_device(self,ports_dict):
		deviceInfos=get_deviceInfo(self.serial)
		self.init_resource(deviceInfos)
		self.connect_cap(ports_dict['minicap_port'])
		self.connect_touch(ports_dict['minitouch_port'])
		self.connect_service([ports_dict['stfservice_port1'],ports_dict['stfservice_port2']])
		db.setDeviceReady(self.serial,ports_dict)
		socketio.emit('change','hehe',namespace='/default')
		db.setDeviceInfo(self.serial,get_deviceInfo(self.serial))
		socketio.emit('change','hehe',namespace='/default')
		print ('iam endddddddddddddddd')
	def init_device(self,ports_dict):
		t1=eventlet.spawn_n(self._init_device,ports_dict)
			



