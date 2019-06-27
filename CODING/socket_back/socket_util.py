import base64
import json
import redis

import config

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

def get_redis():
    redis_pool = redis.ConnectionPool()
    if config.redis['auth']:
        redis_client = redis.Redis(connection_pool=redis_pool, host=config.mongo['url'], port=config.mongo['port'], password=config.redis['password'])
    else:
        redis_client = redis.Redis(connection_pool=redis_pool, host=config.mongo['url'], port=config.mongo['port'])
    return redis_client