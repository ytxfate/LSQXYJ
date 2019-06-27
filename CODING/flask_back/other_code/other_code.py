from flask import Blueprint, request, Response, session
import json

from util import base_operate, send_emails, util_tools

conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()

# 定义模板
other = Blueprint('other',__name__)

@other.route('/register_email_code', methods=['POST'])
def register_email_code():
    email_str = request.json['email_str']
    if email_str and '@' in email_str:
        se = send_emails.SendEmail()
        email_code = util_tools.generate_random_str(randomlength=10)
        html_str = '''
        <div>
            <h3>凉山气象预报预警系统</h3>
            <p>{email} 您好：</p>
            <p>欢迎使用凉山气象预报预警系统</p>
            本次注册验证码：<b style="color:red;">{email_code}</b>
            <p>5 分钟内认证有效，请尽快注册</p>
        </div>
        '''.format(email=email_str, email_code = email_code)
        ret = se.send_eamil(email_str, '用户注册认证', html_str)
        if ret:
            # 将此 email 账号下的 email_code 存到 redis 以便认证
            conn_redis.set(email_str, email_code, ex=320,nx=True)
            return Response(json.dumps({'send_status':'SUCCESS'},ensure_ascii=False), mimetype='application/json')
    return Response(json.dumps({'send_status':'ERROR'},ensure_ascii=False), mimetype='application/json')

@other.route('/get_county', methods=['GET'])
def get_county():
    """
    获取所有的乡
    """
    rows = db_mongo.get_collection('place_name').find({"area" : "county"}, {'_id': 0, 'name': 1})
    ret_list = []
    for row in rows:
        if row['name'] == '城区':
            continue
        ret_list.append(row['name'])
    return Response(json.dumps({'data': ret_list},ensure_ascii=False), mimetype='application/json') 
    
@other.route('/get_township', methods=['GET'])
def get_township():
    """
    获取所有的乡
    """
    county = request.args.get("county") or ''
    rows = db_mongo.get_collection('place_name').find({"area" : "township", "county" : county}, {'_id': 0, 'name': 1})
    ret_list = []
    for row in rows:
        ret_list.append(row['name'])
    return Response(json.dumps({'data': ret_list},ensure_ascii=False), mimetype='application/json') 