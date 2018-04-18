import sys,os
# import subprocess
import time
from eventlet.green import subprocess
# import eventlet
# eventlet.monkey_patch()
def getlogcat(serial):
	command="adb -s %s logcat"%serial
	p=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for line in p.stdout.readlines():
		print (line)
def getDisplayInfo(serial):
	r=call_adb2("-s %s shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -i"%serial)
	try:
		d=eval(''.join(r[1]).replace('true','True'))
		return d
	except:
		return None
def launchApp(serial,package,activity):
	res=call_system('adb -s %s shell am start -n %s/%s'%(serial,package,activity))
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None		
def getpackage(apkPath):
	res=call_system("aapt d badging %s |grep package"%apkPath)
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None
def getActivity(apkPath):
	res=call_system('aapt d badging %s|grep launchable-activity'%apkPath)
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None	
def call_system(command):
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	results=[]
	for line in p.stdout.readlines():  
	    results.append(line.strip().decode('utf-8'))
	    # print (results)
	retval = p.wait()
	return (retval,results)
def call_adb2(command):
	command_text = 'adb %s' % command
	# print (command_text)
	p = subprocess.Popen(command_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	results=[]
	for line in p.stdout.readlines():  
	    results.append(line.strip().decode('utf-8'))
	    # print (results)
	retval = p.wait()
	return (retval,results)
def call_adb_nowait(command):
	command_text = 'adb %s' % command
	p = subprocess.Popen(command_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print (p)
	return True
def exe_shell(serial,command):
	# print (command)
	res=call_adb_nowait("-s %s shell %s"%(serial,command))
	# time.sleep(0.7)
	return res
def exe_shell2(serial,command):
	res=call_adb2("-s %s shell %s"%(serial,command))
def forward(serial,port,commn):
	res=call_adb2("-s %s forward tcp:%s localabstract:%s"%(serial,port,commn))
def forward_tcp(serial,port1,port2):
	res=call_adb_nowait("-s %s forward tcp:%s tcp:%s"%(serial,port1,port2))
	# print ("-s %s forward tcp:%s tcp:%s"%(serial,port1,port2))
def get_abi(serial):
	res= call_adb2("-s '%s' shell getprop ro.product.cpu.abi"%serial)
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None
def get_sdk(serial):
	res= call_adb2("-s '%s' shell getprop gsm.sim.operator.alpha"%serial)
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None
def get_info(serial,infoType):
	res= call_adb2("-s '%s' shell getprop %s"%(serial,infoType))
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None
def get_deviceInfo(serial):
	model = get_info(serial,'ro.product.model')
	brand = get_info(serial,'ro.product.brand')
	print (brand)
	manufacturer = get_info(serial,'ro.product.manufacturer')
	operator = get_info(serial,'gsm.sim.operator.alpha') or get_info(serial,'gsm.operator.alpha')
	version = get_info(serial,'ro.build.version.release')
	sdk = get_info(serial,'ro.build.version.sdk')
	abi = get_info(serial,'ro.product.cpu.abi')
	product = get_info(serial,'ro.product.name')
	pie = '' if sdk and int(sdk)>=16 else '-nopie'
	size=getSize(serial)
	return {'serial': serial
				, 'platform': 'Android'
				, 'manufacturer': manufacturer.upper() if manufacturer else manufacturer
				, 'operator': operator or None
				, 'model': model
				, 'version': version
				, 'abi': abi
				, 'sdk': sdk
				, 'bin': pie
				, 'product': product
				, 'size':size
			}
def get_apk_path(serial,pkgname):
	res=call_adb2("-s %s shell pm path %s"%(serial,pkgname))
	# print (res)
	if res[0]==0 and res[1]:
		return res[1][0].split(':')[-1]
	else:
		return None
def install(serial,pkg):
	res=call_adb2("-s %s install -r %s"%(serial,pkg))
	return res
def uninstall(serial,packageName):
	res=call_adb2("-s %s uninstall %s"%(serial,packageName))
	return res
def install2(serial,localpkg):
	res=call_adb2("-s %s shell pm install -r %s"%(serial,localpkg))
	return res
def push(serial,src,dest,mode='0755'):
	res=call_adb2("-s %s push %s %s  %s"%(serial,src,dest,mode))
	return res
def rm(serial,dest,mode=''):
	res=call_adb2("-s %s shell rm %s %s"%(serial,mode,dest))
	return res
def mkdir(serial,targetdir):
	res=call_adb2("-s %s shell 'mkdir %s 2>/dev/null'"%(serial,targetdir))
	return res
def exists(serial,target):
	res=call_adb2("-s %s shell ls %s"%(serial,target))
	return res
def checkPid(serial,commn):
	res=call_adb2("-s %s shell ps %s"%(serial,commn))
	if len(res[1])<2:
		return None
	else:
		pids=[]
		for result in res[1][1:]:
			pid=result.split(' ')[5]
			pids.append(pid)
		return pids
def kill(serial,commn,mode=15):
	res=call_adb2("-s %s shell ps %s"%(serial,commn))
	if len(res[1])<2:
		return None
	else:
		pids=[]
		for result in res[1][1:]:
			pid=result.split(' ')[5]
			pids.append(pid)
			call_adb2("-s %s shell kill -%s %s"%(serial,mode,pid))
		return pids
def killPid(serial,pid,mode=15):
	call_adb2("-s %s shell kill -%s %s"%(serial,mode,pid))
def getSize(serial):
	res=call_adb2("-s %s shell dumpsys window | grep -Eo 'init=\d+x\d+' | head -1 | cut -d= -f 2"%serial)
	if res[1]:
		return res[1][0]
	else:
		w=call_adb2("-s %s shell dumpsys window | grep -Eo 'DisplayWidth=\d+' | head -1 | cut -d= -f 2"%serial)
		h=call_adb2("-s %s shell dumpsys window | grep -Eo 'DisplayHeight=\d+' | head -1 | cut -d= -f 2"%serial)
		return '%sx%s'%(w,h)
def check_services_Version(serial,apkpath,agentname):
	res=call_adb2("-s %s shell export CLASSPATH='%s'\;exec app_process /system/bin %s --version"%(serial,apkpath,agentname))
	if res[0]==0 and res[1]:
		return res[1][0]
	else:
		return None
def get_devices():
	res=call_adb2('devices')
	device_d={}
	if res[0]==0 and len(res[1])>1:
		deiveslist=res[1][1:]
		for device in deiveslist:
			if device:
				temp=device.split('\t')
				# print (temp,'temp')
				serial=temp[0]
				d={}
				status='online' if temp[1]=='device' else temp[1]
				# d=get_deviceInfo(serial)
				d['status']=status
				device_d[serial]=d
		return device_d
	else:
		return None
def check_minicap():
    width = None
    height = None
    for i in subprocess.Popen("adb shell 'LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -i'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines():
        i=i.decode()
        print (i)
        if 'secure' in i and 'true' in i:
            print('pushsdk:success')
        elif 'width' in i:
            width = i.strip().split(':')[1].strip().split(',')[0]
        elif 'height' in i:
            height = i.strip().split(':')[1].strip().split(',')[0]

    if width is not None:
        return width, height
    return width, height
if __name__=='__main__':
	import time
	s=get_deviceInfo('10fb90b97cf4')
	print (s)
	# print (check_minicap())
	# import platform
	# print (platform.system())
	# abi=get_abi('fa3fb4067d52')
	# print ('abi:',abi)
	# abi_fail=get_abi('fa3fb4067d521')
	# print ('abi_fail:',abi_fail)	
	# sdk=get_sdk('fa3fb4067d52')
	# print ('sdk:',sdk)
	# st=time.time()
	# infos=get_deviceInfo('fa3fb4067d52')
	# print (time.time()-st)
	# print (infos)
	# # res=kill('fa3fb4067d52','minicap')
	# print (res)
	# size=getSize('fa3fb4067d52')
	# print (size)
	# mkdir('fa3fb4067d52','/data/local/tmp/minicap-devel')
	# res=push('BY8HCQIZQSVS9PYS','/Users/xz/MTP/app/vendor/minitouch/arm64-v8a/minitouch','/data/local/tmp/minitouch','')
	# res2=rm('fa3fb4067d52','/data/local/tmp/minicap.so')
	# print (res2)
	# res3=get_apk_path('fa3fb4067d52','jp.co.cyberagent.stf')
	# print (res3)
	# check_services_Version('fa3fb4067d52','/data/app/jp.co.cyberagent.stf-2/base.apk','jp.co.cyberagent.stf.Agent')
	# kill('fa3fb4067d52','minicap')
	# res=exe_shell('fa3fb4067d52','LD_LIBRARY_PATH=%s exec %s %s'%('/data/local/tmp/','/data/local/tmp/minicap',"-P 720x1280@720x1280/0"))
	# res=exe_shell('fa3fb4067d52','exec %s'%'/data/local/tmp/minitouch')
	# print (res)
	# a=forward('fa3fb4067d52',1111,'minitouch')
	# print (a)
	# print (res)
	# d=get_devices()
	# # print (d)
	# res=getpackage('/tmp/uploadforder/20160530-xiaomi-release1473241450139.apk')
	# p=res.split("name='")[1].split("'")[0]
	# res=getActivity('/tmp/uploadforder/20160530-xiaomi-release1473241450139.apk')
	# a= res.split("name='")[1].split("'")[0]
	# # st=time.time()
	# # res2=install('fa3fb4067d52','/tmp/uploadforder/20160530-baidu-release.apk')
	# # print (res2[1][2])
	# print (p,a)
	# # print (time.time()-st)
	# res=launchApp(p,a)
	# print (res)
	# call_adb_nowait('devices')
	# res=getlogcat('fa3fb4067d52')
	# print (getDisplayInfo('fa3fb4067d52'))
	# res3=exists('fa3fb4067d52','/data/local/tmp/minicap-devel/testa.py')
