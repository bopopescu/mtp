from flask import current_app
import crowd


def auth_crowd(username,pwd):
    print (username,pwd)
    cwd=crowd.CrowdServer(current_app.config['CROWD_URL'],current_app.config['CROWD_APP'],current_app.config['CROWD_APPPWD'])
    try:
        user_dict=cwd.auth_user(username,pwd)
        print (user_dict)
        if user_dict is not None:
            return True
        else:
            return False
    except Exception as e:
        print (str(e),'ffff')
        return False

def get_user(username):
    cwd=crowd.CrowdServer(current_app.config['CROWD_URL'],current_app.config['CROWD_APP'],current_app.config['CROWD_APPPWD'])
    try:
        user_dict=cwd.get_user(username)
        if user_dict is not None:
            group=cwd.get_groups(username)
            return {'username':user_dict.get('name'),'displayname':user_dict.get('display-name'),'email':user_dict.get('email'),'groups':str(group)}

        else:
            return None
    except Exception as e:
        return None

