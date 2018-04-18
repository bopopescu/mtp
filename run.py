#!/usr/bin/env python
# from gevent import monkey
# monkey.patch_all()
from app import create_app,db,socketio
from flask_script import Manager
from flask.ext.migrate import Migrate,MigrateCommand
app=create_app('development')
manager=Manager(app)
migrate=Migrate(app,db)
manager.add_command('db', MigrateCommand)




@manager.command
def run():
    # socketio.run(app,host='10.1.58.149',port=7777,debug=False)
    socketio.run(app,host='192.168.160.131',port=7777,debug=False)


if __name__=='__main__':
    #app.run(debug=True,host='192.168.74.35',port=7777)
    manager.run()
