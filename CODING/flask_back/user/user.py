from flask import Blueprint, request, Response, session
import json
import urllib.parse
# 加密
from util import util_tools
from util import base_operate
import uuid

from operator import itemgetter

conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()

# 定义模板
user = Blueprint('user', __name__)


@user.route('/register', methods=['POST'])
def user_register():
    """
    用户注册
    """
    user_info = request.json
    default_keys = set(["username","real_name","password","birthday","sex","addr_provence","addr_zhou","addr_county","addr_township","question","answer","email_code"])
    # 验证注册信息是否填写完善
    if user_info and set(user_info.keys()) == default_keys:
        result = conn_redis.get(user_info['username'])
        # 验证 email_code 是否正确
        if result and result.decode(encoding='utf-8') == user_info['email_code']:
            # 检查用户名是否已经存在
            if db_mongo.get_collection('user').find_one({'username': user_info['username']}):
                return Response(json.dumps({'register_status':'ERROR', 'message': '此邮箱已经被注册，请跟换Email账号'},ensure_ascii=False), mimetype='application/json')
            else:
                # 加密用户密码
                user_info['password'] = util_tools.encrypt_password(user_info['password'])
                del user_info['email_code']
                db_mongo.get_collection('user').insert(user_info)
                return Response(json.dumps({'register_status':'SUCCESS', 'message': '注册成功'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'register_status':'ERROR', 'message': '邮箱验证码不正确，请重新获取'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'register_status':'ERROR', 'message': '注册信息填写不完善'},ensure_ascii=False), mimetype='application/json')

@user.route('/login', methods=['POST'])
def user_login():
    """
    用户登录
    """
    user_info = request.json
    # 验证信息完整性
    if user_info and set(user_info.keys()) == set(['username', 'password']):
        user_info['password'] = util_tools.encrypt_password(user_info['password'])
        row = db_mongo.get_collection('user').find_one(user_info)
        if row:
            ip_addr = request.headers.get('X-Real-IP') or ''
            jwt_str = util_tools.jwt_token(user_info['username'], ip_addr)
            conn_redis.set(user_info['username'], jwt_str,ex=60*30,nx=True)
            return Response(json.dumps({'login_status':'SUCCESS','user_session':jwt_str, 'real_name': row['real_name']},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'login_status':'ERROR', 'message': '用户登录信息验证失败'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'login_status':'ERROR', 'message': '登录信息填写不完善'},ensure_ascii=False), mimetype='application/json')

@user.route('/change_pwd', methods=['POST'])
def user_change_pwd():
    """
    修改密码
    """
    user_info = request.json
    # 验证信息完整性
    if user_info and set(user_info.keys()) == set(['old_pwd', 'new_pwd']):
        token_str = request.cookies.get("user_session")
        if token_str:
            token_str = urllib.parse.unquote(token_str)
            user_payload = util_tools.jwt_token_decode(token_str)
            username = ''
            if user_payload and 'username' in user_payload:
                username = user_payload['username']
            # 加密
            old_pwd = util_tools.encrypt_password(user_info['old_pwd'])
            new_pwd = util_tools.encrypt_password(user_info['new_pwd'])
            if db_mongo.get_collection('user').find_one({'username': username, 'password': old_pwd}):
                db_mongo.get_collection('user').update({
                    'username': username, 'password': old_pwd
                },{
                    '$set': {'password': new_pwd}
                })
                return Response(json.dumps({'change_pwd_status':'SUCCESS', 'message': '用户密码修改成功'},ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps({'change_pwd_status':'ERROR', 'message': '用户信息验证失败，请检查输入的旧密码是否正确！'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'change_pwd_status':'ERROR', 'message': '用户信息获取失败'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'change_pwd_status':'ERROR', 'message': '信息填写不完善'},ensure_ascii=False), mimetype='application/json')

@user.route('/logout', methods=['POST'])
def user_logout():
    """
    登出
    """
    token_str = request.cookies.get("user_session")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        if username:
            if conn_redis.get(username):
                conn_redis.delete(username)
    return Response(json.dumps({'logout':'SUCCESS'},ensure_ascii=False), mimetype='application/json')

@user.route('/get_user_info', methods=['POST'])
def get_user_info():
    """
    获取个人信息
    """
    ret_obj = {}
    token_str = request.cookies.get("user_session")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        ret_obj = db_mongo.get_collection('user').find_one({'username': username}, {'_id':0,'password':0})
    return Response(json.dumps({'data':ret_obj},ensure_ascii=False), mimetype='application/json')

@user.route('/test_user', methods=['POST'])
def test_user():
    """
    测试用户是否登录
    """
    return Response(json.dumps({'user_login_stat':'SUCCESS'},ensure_ascii=False), mimetype='application/json')

@user.route('/change_person_info', methods=['POST'])
def user_change_person_info():
    user_info = request.json
    default_keys = set(["username","real_name","birthday","sex","addr_provence","addr_zhou","addr_county","addr_township","question","answer"])
    # 验证注册信息是否填写完善
    if user_info and set(user_info.keys()) == default_keys:
        username = user_info['username']
        del user_info['username']
        db_mongo.get_collection('user').update({'username': username}, {'$set': user_info})
        return Response(json.dumps({'change_person_info_status':'SUCCESS'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'change_person_info_status':'ERROR', 'message': '信息填写不完善'},ensure_ascii=False), mimetype='application/json')

@user.route('/sub_weather', methods=['POST'])
def user_sub_weather():
    """
    订阅天气信息
    """
    place_info = request.json
    token_str = request.cookies.get("user_session")
    if place_info and set(place_info.keys()) == set(['sub_addr_provence', 'sub_addr_zhou', 'sub_addr_county', 'sub_addr_township']):
        if token_str:
            token_str = urllib.parse.unquote(token_str)
            user_payload = util_tools.jwt_token_decode(token_str)
            username = ''
            if user_payload and 'username' in user_payload:
                username = user_payload['username']
            place_info['username'] = username
            if db_mongo.get_collection('sub_weather').find_one(place_info):
                return Response(json.dumps({'sub_status':'ERROR', 'message': '你已订阅该地区的气象信息'},ensure_ascii=False), mimetype='application/json')
            elif db_mongo.get_collection('sub_weather').find({'username': username}).count() >= 5:
                return Response(json.dumps({'sub_status':'ERROR', 'message': '你订阅的地区气象信息过多，请删除部分订阅地区后再订阅其他地区！'},ensure_ascii=False), mimetype='application/json')
            else:
                place_info['pri_key'] = str(uuid.uuid1())
                db_mongo.get_collection('sub_weather').insert(place_info)
                return Response(json.dumps({'sub_status':'SUCCESS', 'message': '订阅成功。'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'sub_status':'ERROR', 'message': '信息填写不完善'},ensure_ascii=False), mimetype='application/json')

@user.route('/get_sub_weather', methods=['POST'])
def user_get_sub_weather():
    """
    查询用户订阅的天气信息
    """
    ret_obj = []
    token_str = request.cookies.get("user_session")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        rows = db_mongo.get_collection('sub_weather').find({'username': username},{'_id':0})
        for row in rows:
            ret_obj.append(row)
    return Response(json.dumps({'sub_data': ret_obj},ensure_ascii=False), mimetype='application/json')

@user.route('/del_sub_weather', methods=['POST'])
def user_del_sub_weather():
    """
    删除用户订阅的天气信息
    """
    place_info = request.json
    token_str = request.cookies.get("user_session")
    if place_info and 'pri_key' in place_info:
        if token_str:
            token_str = urllib.parse.unquote(token_str)
            user_payload = util_tools.jwt_token_decode(token_str)
            username = ''
            if user_payload and 'username' in user_payload:
                username = user_payload['username']
            place_info['username'] = username
            db_mongo.get_collection('sub_weather').delete_one(place_info)
            return Response(json.dumps({'del_status': 'SUCCESS'},ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps({'del_status': 'ERROE'},ensure_ascii=False), mimetype='application/json')
