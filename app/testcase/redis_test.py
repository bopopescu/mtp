import redis
r = redis.StrictRedis(host='10.2.1.67', port=6379, db=0,decode_responses=True)
print ('end')
def getAvaliableDevices():
	devicelist=[]
	devices=r.hgetall("allDevices")
	for device in sorted(devices.items(),key=lambda x:x[1],reverse=True):
		if device[1]=='ready':
			infos=getDeviceInfos(device[0])
			print (infos,'infos',device[0])
			devicelist.append({'serial':device[0],'screen':infos['size'],'manufacturer':infos['manufacturer']})
	return devicelist
def getDeviceInfos(serial):
	return r.hgetall('device:%s'%serial)
# r = redis.StrictRedis(host='10.1.40.31', port=6379, db=0,decode_responses=True)

print (r.keys())
print ('a2')
# r.hset("allDevices","a3","aa")
# dic={"a1":"ab","a12":"bb"}
# print(r.hvals("allDevices"))
# print(r.hkeys("allDevices"))
# # # print(r.hget("allDevices","a12"))
# # d={}
# m=r.hget("allDevices",'7cfcbea7')
# # print (m)
# for i in sorted(m.items(),key=lambda x:x[1],reverse=True):
# 	if i[1]!='offline' and i[1]!='preparing':
# 		d[i[0]]=r.hgetall('device:%s'%i[0])
# print (d)
# r.hdel('allDevices')
# print(m)
# n=r.hgetall("device:7cfcbea7")
# n2=r.hgetall("device:7cfcbea7")
# displayinfos=n.get('display')
# # print (n['display']['rotation'])
# print (n)
# print (n2)
# print (getAvaliableDevices())
# hdel('allDevices')
# print (sorted(m.items(),key=lambda a:a[1],reverse=True))
# print (r.keys())
# print(r.hexists("allDevices","a11"))
# print (r.flushdb())
# import json
# a={b'a':b'b'}
# print (a)
# print (json.loads(a))
# r.hdel("device:","uid")
