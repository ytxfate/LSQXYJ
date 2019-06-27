from flask import Blueprint, request, Response
import json
import re
import time

# 定义模板
centos = Blueprint('centos',__name__)

@centos.route('/get_memery_info', methods=['GET'])
def get_memery_info():
    mem_info = {}
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
            name = line.split(':')[0]
            val = line.split(':')[1].replace('\n','').strip().split()[0]
            mem_info[name] = int(val)
    mem_info['MemUsed'] = mem_info['MemTotal'] - mem_info['MemFree'] - mem_info['Buffers'] - mem_info['Cached']
    return Response(json.dumps(mem_info,ensure_ascii=False), mimetype='application/json')

# psutil库netifaces
@centos.route('/get_cpu_info', methods=['GET'])
def get_cpu_info():
    with open('/proc/stat', 'r') as f:
        line_1 = f.readline()
        cpu_time_list = re.findall(r'\d+', line_1)
        cpu_idle1 = int(cpu_time_list[3])
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)
    time.sleep(1.5)
    with open('/proc/stat', 'r') as f_2:
        line_2 = f_2.readline()
        cpu_time_list_2 = re.findall(r'\d+', line_2)
        cpu_idle2 = int(cpu_time_list_2[3])
        total_cpu_time2 = 0
        for t in cpu_time_list_2:
            total_cpu_time2 = total_cpu_time2 + int(t)
    cpu_usage = 1 - (cpu_idle2 - cpu_idle1) / (total_cpu_time2 - total_cpu_time1)
    return Response(json.dumps({"cpu_use":cpu_usage},ensure_ascii=False), mimetype='application/json')


# 内存信息 / meminfo
def memory_stat():
    mem_info = {}
    with open('/proc/meminfo') as f:
        lines = f.readlines()
        for line in lines:
            name = line.split(':')[0]
            val = line.split(':')[1].replace('\n','').strip().split()[0]
            mem_info[name] = int(val)
    mem_info['MemUsed'] = mem_info['MemTotal'] - mem_info['MemFree'] - mem_info['Buffers'] - mem_info['Cached']
    return mem_info

# CPU信息 / cpuinfo
def cpu_stat():
    cpu = []
    cpuinfo = {}
    f = open("/proc/cpuinfo")
    lines = f.readlines()
    f.close()
    for line in lines:
        if line == '\n':
            cpu.append(cpuinfo)
            cpuinfo = {}
        if len(line) < 2: continue
        name = line.split(':')[0].rstrip()
        var = line.split(':')[1]
        cpuinfo[name] = var
    return cpu

# 负载信息 / loadavg
def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg

# 运转时间 / Uptime
def uptime_stat():
    uptime = {}
    f = open("/proc/uptime")
    con = f.read().split()
    f.close()
    all_sec = float(con[0])
    MINUTE,HOUR,DAY = 60,3600,86400
    uptime['day'] = int(all_sec / DAY )
    uptime['hour'] = int((all_sec % DAY) / HOUR)
    uptime['minute'] = int((all_sec % HOUR) / MINUTE)
    uptime['second'] = int(all_sec % MINUTE)
    uptime['Free rate'] = float(con[1]) / float(con[0])
    return uptime

# 获取网卡流量信息 /proc/net/dev
def net_stat():
    net = []
    f = open("/proc/net/dev")
    lines = f.readlines()
    f.close()
    for line in lines[2:]:
        con = line.split()
        """
        intf = {}
        intf['interface'] = con[0].lstrip(":")
        intf['ReceiveBytes'] = int(con[1])
        intf['ReceivePackets'] = int(con[2])
        intf['ReceiveErrs'] = int(con[3])
        intf['ReceiveDrop'] = int(con[4])
        intf['ReceiveFifo'] = int(con[5])
        intf['ReceiveFrames'] = int(con[6])
        intf['ReceiveCompressed'] = int(con[7])
        intf['ReceiveMulticast'] = int(con[8])
        intf['TransmitBytes'] = int(con[9])
        intf['TransmitPackets'] = int(con[10])
        intf['TransmitErrs'] = int(con[11])
        intf['TransmitDrop'] = int(con[12])
        intf['TransmitFifo'] = int(con[13])
        intf['TransmitFrames'] = int(con[14])
        intf['TransmitCompressed'] = int(con[15])
        intf['TransmitMulticast'] = int(con[16])
        """
        intf = dict(
            zip(
                ( 'interface','ReceiveBytes','ReceivePackets',
                  'ReceiveErrs','ReceiveDrop','ReceiveFifo',
                  'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',
                  'TransmitBytes','TransmitPackets','TransmitErrs',
                  'TransmitDrop', 'TransmitFifo','TransmitFrames',
                  'TransmitCompressed','TransmitMulticast' ),
                ( con[0].rstrip(":"),int(con[1]),int(con[2]),
                  int(con[3]),int(con[4]),int(con[5]),
                  int(con[6]),int(con[7]),int(con[8]),
                  int(con[9]),int(con[10]),int(con[11]),
                  int(con[12]),int(con[13]),int(con[14]),
                  int(con[15]),int(con[16]), )
            )
        )
 
        net.append(intf)
    return net

# # 磁盘空间使用
# import os, sys
# def disk_stat():
#     import os
#     hd={}
#     disk = os.statvfs("/")
#     hd['available'] = disk.f_bsize * disk.f_bavail
#     hd['capacity'] = disk.f_bsize * disk.f_blocks
#     hd['used'] = disk.f_bsize * disk.f_bfree
#     return hd

# import pprint
# if __name__ == "__main__":
#     print('=====================================================')
#     # 内存信息 / meminfo
#     m = memory_stat()
#     pprint.pprint(m)
#     print('=====================================================')
#     # CPU信息 / cpuinfo
#     c = cpu_stat()
#     print(c)
#     print('=====================================================')
#     # 负载信息 / loadavg
#     l = load_stat()
#     print(l)
#     print('=====================================================')
#     # 运转时间 / Uptime
#     u = uptime_stat()
#     print(u)
#     print('=====================================================')
#     # 获取网卡流量信息 /proc/net/dev
#     n = net_stat()
#     print(n)
#     print('=====================================================')
#     # 磁盘空间使用
#     d = disk_stat()
#     print(d)
