from .. import redis as r

def getAvaliableDevices():
	try:
		devicelist=[]
		devices=r.hgetall("allDevices")
		for device in sorted(devices.items(),key=lambda x:x[1],reverse=True):
			if device[1]=='ready':
				infos=getDeviceInfos(device[0])
				devicelist.append({'serial':device[0],'screen':infos.get('size'),'manufacturer':infos.get('manufacturer')})
	except Exception as e:
		print (str(e))
		print (devices)
		return []
	return devicelist
def getDeviceInfos(serial):
	return r.hgetall('device:%s'%serial)
def getAllDevices(uid):
	devices=r.hgetall("allDevices")
	d={}
	for device in sorted(devices.items(),key=lambda x:x[1],reverse=True):
		serial=device[0]
		status=device[1]
		if status=='ready' or status=='busy':
			d[serial]=r.hgetall('device:%s'%device[0])
			if uid and d[serial].get('uid')==str(uid):
				d[device[0]]['status']='Stop Using'
			elif status=='busy':
				d[device[0]]['status']='busy'
			else:
				d[device[0]]['status']='Use'
		else:
			d[serial]={'status':status}
	return d
def getAllDeviceSerials():
	return r.hkeys("allDevices")
def addDevices(deviceList):
	for device in deviceList:
		addDevice(device)
def addDevice(serial):
	print (serial,'serial')
	r.hset('allDevices',serial,'preparing')
def initDevices():
	devices=[device for device in r.hkeys('allDevices') if r.hget("allDevices",device)!='offline']
	removeDevices(devices)
	
def removeDevices(deviceList):
	print (deviceList,'list')
	for device in deviceList:
		setDeviceOffline(device)

def setDeviceOffline(serial):
	r.hset('allDevices',serial,'offline')
	keys=r.hkeys("device:%s"%serial)
	for key in keys:
		r.hdel("device:%s"%serial,key)

def setDeviceError(serial):
	# print ('setError')
	r.hset('allDevices',serial,'error')
	# keys=r.hkeys("device:%s"%serial)
	# for key in keys:
	# 	r.hdel("device:%s"%serial,key)
def setDeviceReady(serial):
	r.hset('allDevices',serial,'ready')

def setDeviceBusy(serial,uid,username):
	dic={'uid':uid,'username':username}
	r.hmset("device:%s"%serial,dic)
	r.hset('allDevices',serial,'busy')
	r.lpush('User:%s'%uid,serial)

def setDeviceAvailable(serial,uid):
	print ('setDeviceAvailable')
	r.hdel("device:%s"%serial,"uid")
	r.hdel("device:%s"%serial,"username")
	r.hset('allDevices',serial,'ready')
	r.lrem('User:%s'%uid,0,serial)

def isDeviceStatus(serial,status='ready'):
	m=r.hget("allDevices",serial)
	if m and m==status:
		return True
	else:
		return False
def getDeviceCurrentUser(serial):
	return r.hget('device:%s'%serial,'uid')


def setDeviceInfo(serial,infos):
	r.hmset("device:%s"%serial,infos)