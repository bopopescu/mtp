from flask import Blueprint
from .manager import supportManager
from .provider  import Provider
import eventlet
testcase=Blueprint('testcase',__name__)
m=supportManager()
print ('m')
sidWithSerialMap={}
cacheMap2={}
p=Provider(m)
eventlet.spawn(p.loop)
# print ('hheheheheheh')
from . import views,actionViews,devicesViews,multiViews
