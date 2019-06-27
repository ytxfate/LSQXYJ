import hashlib
import base64
import time
import json


def encrypt_password(pwd_str):
    """
    密码加密
    """
    # 1.创建一个hash对象
    h = hashlib.sha256()
    # 2.填充要加密的数据
    h.update(bytes(pwd_str, encoding='utf-8'))
    # 3.获取加密结果
    pawd_result = h.hexdigest()
    return pawd_result

def jwt_token(username, ip_addr):
    """
    token 认证
    """
    jwt_header = {
        'typ': 'JWT',
        'alg': 'sha256'
    }
    jwt_header_encode = base64.b64encode(str(jwt_header).encode(encoding='utf-8'))
    jwt_payload = {
        'username': username,
        'time': time.time(),
        'ip': ip_addr
    }
    jwt_payload_encode = base64.b64encode(str(jwt_payload).encode(encoding='utf-8'))
    jwt_signature = encrypt_password(jwt_header_encode.decode('utf-8') + '.' + jwt_payload_encode.decode('utf-8'))
    jwt_str = jwt_header_encode.decode('utf-8') + '.' + jwt_payload_encode.decode('utf-8') + '.' + jwt_signature
    return jwt_str

def jwt_token_decode(jwt_str):
    """
    解密 JWT, 提取信息
    """
    jwts = jwt_str.split('.')
    if len(jwts) == 3:
        jwt_payload_encode = jwts[1]
        jwt_payload_str = base64.b64decode(jwt_payload_encode).decode('utf-8')
        jwt_payload = json.loads(jwt_payload_str.replace("'",'"'))
        return jwt_payload
    return None

import random
import string
def generate_random_str(randomlength=16):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_letters=abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
    """
    str_list = [random.choice(string.digits + string.ascii_letters) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str