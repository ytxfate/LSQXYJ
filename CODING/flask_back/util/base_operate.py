import pymongo
import redis

import config

def get_mongodb():
    # mongo
    conn_mongo = pymongo.MongoClient(host=config.mongo['url'],port=config.mongo['port'])
    db_mongo = conn_mongo.get_database(config.mongo['db'])
    if config.mongo['auth']:
        db_mongo.authenticate(name=config.mongo['username'], password=config.mongo['password'])
    return conn_mongo, db_mongo

# def get_redis_old():
#     # redis
#     if config.redis['auth']:
#         redis_pool = redis.ConnectionPool(host=config.mongo['url'], port=config.mongo['port'], password=config.redis['password'])
#     else:
#         redis_pool = redis.ConnectionPool(host=config.mongo['url'], port=config.mongo['port'])
#     redis_client = redis.Redis(connection_pool=redis_pool)
#     return redis_client

def get_redis():
    redis_pool = redis.ConnectionPool()
    if config.redis['auth']:
        redis_client = redis.Redis(connection_pool=redis_pool, host=config.mongo['url'], port=config.mongo['port'], password=config.redis['password'])
    else:
        redis_client = redis.Redis(connection_pool=redis_pool, host=config.mongo['url'], port=config.mongo['port'])
    return redis_client