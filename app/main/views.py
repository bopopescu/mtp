from flask import render_template,flash,request
from . import main
from flask.ext.login import login_required,login_user,current_user,logout_user
from ..models import User

@main.route('/',methods=['GET','POST'])
# @login_required
def index():
	print (request.data)
	print ('fuck')
	user=User.query.filter_by(username='xuzhao').first()
	print (user.email)
	return render_template('index.html')
