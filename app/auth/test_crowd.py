import crowd
# from flask import current_app
# ip='http://180.150.184.115:8095/crowd/'
ip='http://10.2.1.12:8095/crowd/'
cwd=crowd.CrowdServer(ip,'testapp','123456')
user_dict=cwd.auth_user('xuzhao','xz123456')
print (user_dict)
print (cwd)
print (cwd.auth_user('xuzhao','xz123456'))


print (cwd.get_nested_groups('xuzhao'))
