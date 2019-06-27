from flask import Flask, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import time
import random
import datetime
import json

app = Flask(__name__)

socketio =  SocketIO()
socketio.init_app(app)

import centos
import socket_util

conn_redis = socket_util.get_redis()

@socketio.on('connect')
def socket_connect():
    print('================= connect =====================')
    net_info = centos.net_stat()
    conn_redis.hset('centos_net.hash', 'net', json.dumps(net_info))

@socketio.on('disconnect')
def socket_disconnect():
    print('================= disconnect =====================')
    pass

@socketio.on('centos_all_info')
def get_centos_all_info(data):
    # 用户验证
    session_id = data.get('session_id')
    jwt_payload = socket_util.jwt_token_decode(session_id)
    username = ''
    if jwt_payload and 'username' in jwt_payload:
        username = jwt_payload['username']
    result = conn_redis.get(username)
    ip = request.headers.get('X-Real-IP') or ''
    if result and 'ip' in jwt_payload and ip == jwt_payload['ip']:
        time.sleep(1)
        dict_end = {}
        # cpu
        cpu_info = centos.get_cpu_info()
        dict_end['cpu'] = cpu_info['cpu_use']
        # memery
        mem_info = centos.get_memery_info()
        dict_end['mem'] = mem_info['MemUsed']/mem_info['MemTotal']
        # load_avg
        load_info = centos.load_stat()
        dict_end['loadavg'] = load_info['lavg_1']
        # uptime
        uptime_info = centos.uptime_stat()
        dict_end['uptime'] = uptime_info
        # net
        ret_net = conn_redis.hget('centos_net.hash', 'net')
        tmp_net_info = {}
        if ret_net:
            tmp_net_info = json.loads(ret_net.decode(encoding='utf-8'))
        else:
            tmp_net_info = centos.net_stat()
            time.sleep(1)
        net_info = centos.net_stat()
        conn_redis.hset('centos_net.hash', 'net', json.dumps(net_info))
        Receive = float(net_info['ReceiveBytes']) - float(tmp_net_info['ReceiveBytes'])
        Transmit = float(net_info['TransmitBytes']) - float(tmp_net_info['TransmitBytes'])
        dict_end['net'] = {'Receive': Receive, 'Transmit': Transmit}
        # disk
        hd_info = centos.disk_stat()
        dict_end['disk'] = hd_info['used'] / hd_info['total']
        emit('ret_info', {'code': 'success', 'msg': dict_end, 'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    else:
        emit('ret_info', {'code': 'error', 'msg': '用户登录验证错误！'})
    return

if __name__ == "__main__":
    socketio.run(app, debug=True, host='127.0.0.1', port=5552)