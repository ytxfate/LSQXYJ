from flask import Flask, session, request, redirect, Response
from flask_cors import CORS
import json

import urllib.parse

from util import util_tools, base_operate

conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()

app = Flask(__name__)
app.secret_key = '123456'
# 跨域
CORS(app, supports_credentials=True)

# 注册蓝图
from search_controllers.search import search
app.register_blueprint(search,url_prefix='/search')
# from centos.centos import centos
# app.register_blueprint(centos,url_prefix='/centos')
from admin.admin import admin
app.register_blueprint(admin, url_prefix='/admin')
from user.user import user
app.register_blueprint(user, url_prefix='/user')
from other_code.other_code import other
app.register_blueprint(other, url_prefix='/other')
from user.usr_oth import usr_oth
app.register_blueprint(usr_oth, url_prefix='/usr_oth')

@app.before_request
def before_request():
    """
    拦截器
    """
    path = request.path
    ip = request.headers.get('X-Real-IP') or ''
    # 管理员
    if ('/admin/' in path) and ('/admin/login' != path) or ('/centos' in path):
        token_str = request.cookies.get("session_id")
        if token_str:
            token_str = urllib.parse.unquote(token_str)
            user_payload = util_tools.jwt_token_decode(token_str)
            username = ''
            if user_payload and 'username' in user_payload:
                username = user_payload['username']
            else:
                return Response(json.dumps({'login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
            result = conn_redis.get(username)
            if result:
                if 'ip' in user_payload and ip == user_payload['ip']:
                    pass
                else:
                    return Response(json.dumps({'login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps({'login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
    # 普通用户
    elif ('user' in path) and ('user/register' not in path) and ('user/login' not in path):
        token_str = request.cookies.get("user_session")
        if token_str:
            token_str = urllib.parse.unquote(token_str)
            user_payload = util_tools.jwt_token_decode(token_str)
            username = ''
            if user_payload and 'username' in user_payload:
                username = user_payload['username']
            else:
                return Response(json.dumps({'user_login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
            result = conn_redis.get(username)
            if result:
                if 'ip' in user_payload and ip == user_payload['ip']:
                    pass
                else:
                    return Response(json.dumps({'user_login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps({'user_login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'user_login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')
    else:
        pass


server_cfg = {
    'host': '127.0.0.1',
    'port': 5550,
    'debug': True
}

if __name__ == '__main__':
    app.run(host=server_cfg['host'], port=server_cfg['port'], debug=server_cfg['debug'])
