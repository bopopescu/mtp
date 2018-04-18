from flask import render_template,redirect,flash,request,url_for
from flask.ext.login import login_required,login_user,current_user,logout_user
from . import auth
from .. import db
from ..models import User
from .auth_crowd import auth_crowd,get_user
from .forms import LoginForm
import datetime


@auth.route('/login',methods=['GET','POST'])
def login():
    print (current_user,'current_user')
    form=LoginForm()
    if form.validate_on_submit():
        if auth_crowd(form.username.data,form.password.data):
            print ('fuck')
            u=get_user(form.username.data)
            if u is not None:
                user=User.query.filter_by(username=form.username.data).first()
                if user is None:
                    user=User(username=u['username'],displayname=u['displayname'],email=u['email'],groups=u['groups'])
                    print (user.displayname)
                    db.session.add(user)
                    db.session.commit()
                login_user(user,form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password!')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
