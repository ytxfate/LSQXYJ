from flask import Blueprint, request, Response, session
import json
import re
import time
import datetime
# 加密
from util import util_tools
from util import base_operate

from operator import itemgetter
import redis
import urllib.parse
import requests


conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()
# redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
# conn_redis = redis.Redis(connection_pool=redis_pool)

# 定义模板
admin = Blueprint('admin',__name__)

# 登录拦截
@admin.route('/get_login_status', methods=['GET', 'POST'])
def get_login_status():
    token_str = request.cookies.get("session_id")
    username = ''
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
    return Response(json.dumps({'login_stat':'SUCCESS','username': username},ensure_ascii=False), mimetype='application/json')

@admin.route('/login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username and password:
        new_password = util_tools.encrypt_password(password)
        collection = db_mongo.get_collection('user_admin')
        row = collection.find_one({"username": username},{'_id':0,"password":1})
        if row:
            if 'password' in row and row['password'] == new_password:
                ip = request.headers.get('X-Real-IP') or ''
                token_str = util_tools.jwt_token(username, ip)
                conn_redis.set(username, token_str,ex=60*30,nx=True)
                # conn_redis.expire(token_str, 10)
                # 更新用户登录信息
                resp = requests.get('http://ip.cz88.net/data.php?ip=' + ip)
                reg_exp = re.compile(r"ShowIPAddr\('(.*?)','(.*?),'(.*?)'\);")
                reg_rlt = reg_exp.match(resp.text)
                print(username + '' + reg_rlt.group(1) + '' + reg_rlt.group(2))
                db_mongo.get_collection('admin_login_info').insert({'username': username, 'ip': ip, 'addr': reg_rlt.group(2), 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                return Response(json.dumps({'login_stat':'SUCCESS','session_id':token_str},ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps({'login_stat':'ERROR'},ensure_ascii=False), mimetype='application/json')


# 数据采集详情
@admin.route('/collect_detail', methods=['GET'])
def collect_detail():
    now_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    row = db_mongo.get_collection('scrapy_stats').find_one({'date': now_date_str}, {'_id': 0}) or {}
    return Response(json.dumps(row, ensure_ascii=False), mimetype='application/json')

# 修改密码
@admin.route('/change_password', methods=['POST'])
def change_password():
    old_pwd = request.form['old_pwd']
    new_pwd = request.form['new_pwd']
    token_str = request.cookies.get("session_id")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        else:
            return Response(json.dumps({'stats':"NOLOGIN", 'msg': '用户登录信息监测失败，请重新登录！'}, ensure_ascii=False), mimetype='application/json')
        result = conn_redis.get(username)
        if result:
            ip = request.headers.get('X-Real-IP') or ''
            if 'ip' in user_payload and ip == user_payload['ip']:
                # check pwd
                old_pwd_new = util_tools.encrypt_password(old_pwd)
                new_pwd_new = util_tools.encrypt_password(new_pwd)
                if db_mongo.get_collection('user_admin').find_one({"username": user_payload['username'], 'password': old_pwd_new}):
                    # check ok
                    db_mongo.get_collection('user_admin').update_one({"username": user_payload['username'], 'password': old_pwd_new},{'$set':{'password': new_pwd_new}})
                    return Response(json.dumps({'stats':"SUCCESS"}, ensure_ascii=False), mimetype='application/json')
                else:   # check error
                    return Response(json.dumps({'stats':"ERROR", 'msg': '用户名或密码验证错误！'}, ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps({'stats':"NOLOGIN", 'msg': '用户登录信息监测失败，请重新登录！'}, ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'stats':"NOLOGIN", 'msg': '用户登录已过期，请重新登录！'}, ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'stats':"NOLOGIN", 'msg': '用户登录已过期，请重新登录！'}, ensure_ascii=False), mimetype='application/json')

# 退出登录 login_out
@admin.route('/login_out', methods=['POST'])
def login_out():
    token_str = request.cookies.get("session_id")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        if conn_redis.get(username):
            conn_redis.delete(username)
    return Response(json.dumps({'login_out_status': 'true'}, ensure_ascii=False), mimetype='application/json')

# 获取用户登录信息
@admin.route('/get_login_info', methods=['get'])
def get_login_info():
    token_str = request.cookies.get("session_id")
    if token_str:
        token_str = urllib.parse.unquote(token_str)
        user_payload = util_tools.jwt_token_decode(token_str)
        username = ''
        if user_payload and 'username' in user_payload:
            username = user_payload['username']
        result = conn_redis.get(username)
        if result:
            rows = db_mongo.get_collection('admin_login_info').find({'username': username}, {'_id': 0}).sort('date', -1).limit(2)
            list_end = []
            for row in rows:
                list_end.append(row)
            list_end = sorted(list_end, key=itemgetter('date'), reverse=True)
            return Response(json.dumps(list_end, ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')

# 获取采集的信息
@admin.route('/get_collect_info', methods=['get'])
def get_collect_info():
    rows = db_mongo.get_collection('scrapy_stats').find({},{'_id':0}).sort('date', -1).limit(1)
    dict_end = {}
    for row in rows:
        dict_end = row
    return Response(json.dumps(dict_end, ensure_ascii=False), mimetype='application/json')