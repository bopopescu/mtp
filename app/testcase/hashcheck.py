import hashlib,time

def checkhash(timestamp=0,key='a',sign='abc'):
	try:
		currentTime=int(time.time()*1000)
		# if currentTime-int(timestamp)>1500:
		# 	return False
		checkStr='%ssaltsalt%s'%(timestamp,key)
		m = hashlib.md5()
		m.update(checkStr.encode('utf-8'))
		psw = m.hexdigest()
	except Exception as e:
		return False
	if psw==sign:
		return True
	else:
		return False
def gethash(timestamp=0,key='a'):
		s='%ssaltsalt%s'%(timestamp,key)
		m = hashlib.md5()
		m.update(s.encode('utf-8'))
		psw = m.hexdigest()
		return psw