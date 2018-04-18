from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,PasswordField,BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    username=StringField('Username', validators=[Required()],id="username")
    password=PasswordField('Password', validators=[Required()])
    remember_me=BooleanField('Remember my login on this computer')
    submit=SubmitField('Log In')



