from .adbkit import *
import time

import eventlet
eventlet.monkey_patch()
def haha2(apkPath):
	eventlet.spawn_n(installApk2,apkPath)

def installApk2(apkPath):
	print ('iamin')
	# return

	try:
		packageName=getpackage(apkPath)
		activity=getActivity(apkPath)
	except:
		# emit('res','get package failed')
		print ('get package failed')
	try:
		res2=install('fa3fb4067d52','/tmp/uploadforder/20160530-baidu-release.apk')
		if res2[1][2]!='Success':
			# emit('res','install failed')
			print ('install failed')
		else:
			# emit('res','install success')
			print ('install success')
		res=launchApp(p,a)
		if res.startwith('Starting'):
			# emit('res','launch success')
			print ('launch success')
		else:
			print ('launch failed')
			# emit('res','launch failed')
	except:
		print ('install failed2')
		# emit('res','install failed')


