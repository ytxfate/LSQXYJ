from flask import Blueprint, request, Response, session
import json
import urllib.parse
# 加密
from util import util_tools
from util import base_operate
from util import send_emails
import uuid

from operator import itemgetter

conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()

# 定义模板
usr_oth = Blueprint('usr_oth', __name__)

@usr_oth.route('get_usr_mibao', methods=['POST'])
def get_usr_mibao():
    """
    获取用户密保
    """
    user_info = request.json
    if user_info and 'username' in user_info:
        row = db_mongo.get_collection('user').find_one(
            {'username': user_info['username']},
            {'_id':0,'question':1}
        )
        if row:
            return Response(json.dumps({'get_mibao_status': 'SUCCESS','data': row},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'get_mibao_status': 'ERROR','message': '没有此用户。'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'get_mibao_status':'ERROR', 'message': '用户信息填写不完善。'},ensure_ascii=False), mimetype='application/json')

@usr_oth.route('check_usr_mibao', methods=['POST'])
def check_usr_mibao():
    """
    验证用户密保
    """
    user_info = request.json
    default_keys = set(["username","question","answer"])
    # 验证注册信息是否填写完善
    if user_info and set(user_info.keys()) == default_keys:
        if db_mongo.get_collection('user').find_one(user_info):
            # 发送邮件
            se = send_emails.SendEmail()
            email_code = util_tools.generate_random_str(randomlength=10)
            html_str = '''
            <div>
                <h3>凉山气象预报预警系统</h3>
                <p>{email} 您好：</p>
                <p>欢迎使用凉山气象预报预警系统</p>
                你的新密码为：<b style="color:red;">{email_code}</b>
                <p>请尽快尽快修改密码</p>
            </div>
            '''.format(email=user_info['username'], email_code = email_code)
            ret = se.send_eamil(user_info['username'], '用户找回密码', html_str)
            if ret:
                # 更新用户新密码
                new_pwd = util_tools.encrypt_password(email_code)
                db_mongo.get_collection('user').update(user_info,{'$set':{'password': new_pwd}})
                return Response(json.dumps({'check_mibao_status': 'SUCCESS', 'message': '新密码已发送到用户邮箱请注意查收并尽快修改密码。'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'check_mibao_status': 'ERROR','message': '用户信息验证错误。'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'check_mibao_status':'ERROR', 'message': '用户信息填写不完善。'},ensure_ascii=False), mimetype='application/json')

@usr_oth.route('get_email_code', methods=['POST'])
def get_email_code():
    """
    通过邮箱验证码找回密码
    """
    user_info = request.json
    default_keys = set(["username"])
    # 验证注册信息是否填写完善
    if user_info and set(user_info.keys()) == default_keys:
        if db_mongo.get_collection('user').find_one(user_info):
            # 发送邮件
            se = send_emails.SendEmail()
            email_code = util_tools.generate_random_str(randomlength=10)
            html_str = '''
            <div>
                <h3>凉山气象预报预警系统</h3>
                <p>{email} 您好：</p>
                <p>欢迎使用凉山气象预报预警系统</p>
                本次找回密码的验证码为：<b style="color:red;">{email_code}</b>
                <p>5 分钟内认证有效，请尽快注册</p>
            </div>
            '''.format(email=user_info['username'], email_code = email_code)
            ret = se.send_eamil(user_info['username'], '用户找回密码', html_str)
            if ret:
                # 将此 email 账号下的 email_code 存到 redis 以便认证
                conn_redis.set(user_info['username'], email_code, ex=320,nx=True)
                return Response(json.dumps({'email_code_status': 'SUCCESS', 'message': '邮箱验证码已发送到用户邮箱请注意查收。'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'email_code_status': 'ERROR','message': '用户信息验证错误。'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'email_code_status':'ERROR', 'message': '用户信息填写不完善。'},ensure_ascii=False), mimetype='application/json')

@usr_oth.route('check_email_code', methods=['POST'])
def check_email_code():
    """
    验证邮箱验证码
    """
    user_info = request.json
    default_keys = set(["username","email_code"])
    # 验证注册信息是否填写完善
    if user_info and set(user_info.keys()) == default_keys:
        # 验证 email_code
        result = conn_redis.get(user_info['username'])
        # 验证 email_code 是否正确
        if result and result.decode(encoding='utf-8') == user_info['email_code']:
            if db_mongo.get_collection('user').find_one({'username':user_info['username']}):
                # 发送邮件
                se = send_emails.SendEmail()
                email_code = util_tools.generate_random_str(randomlength=10)
                html_str = '''
                <div>
                    <h3>凉山气象预报预警系统</h3>
                    <p>{email} 您好：</p>
                    <p>欢迎使用凉山气象预报预警系统</p>
                    你的新密码为：<b style="color:red;">{email_code}</b>
                    <p>请尽快尽快修改密码</p>
                </div>
                '''.format(email=user_info['username'], email_code = email_code)
                ret = se.send_eamil(user_info['username'], '用户找回密码', html_str)
                if ret:
                    # 更新用户新密码
                    new_pwd = util_tools.encrypt_password(email_code)
                    db_mongo.get_collection('user').update({'username':user_info['username']},{'$set':{'password': new_pwd}})
                    return Response(json.dumps({'check_code_status': 'SUCCESS', 'message': '新密码已发送到用户邮箱请注意查收并尽快修改密码。'},ensure_ascii=False), mimetype='application/json')
            else:
                return Response(json.dumps({'check_code_status': 'ERROR','message': '用户信息验证错误。'},ensure_ascii=False), mimetype='application/json')
        else:
            return Response(json.dumps({'check_mibao_status': 'ERROR','message': '邮箱验证码信息验证错误。'},ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps({'check_code_status':'ERROR', 'message': '用户信息填写不完善。'},ensure_ascii=False), mimetype='application/json')
