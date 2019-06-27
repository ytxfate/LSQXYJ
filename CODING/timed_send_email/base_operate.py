import pymongo

import config

def get_mongodb():
    # mongo
    conn_mongo = pymongo.MongoClient(host=config.mongo['url'],port=config.mongo['port'])
    db_mongo = conn_mongo.get_database(config.mongo['db'])
    if config.mongo['auth']:
        db_mongo.authenticate(name=config.mongo['username'], password=config.mongo['password'])
    return conn_mongo, db_mongo
