import json
import re
import time

def get_memery_info():
    mem_info = {}
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        for line in lines:
            name = line.split(':')[0]
            val = line.split(':')[1].replace('\n','').strip().split()[0]
            mem_info[name] = int(val)
    mem_info['MemUsed'] = mem_info['MemTotal'] - mem_info['MemFree'] - mem_info['Buffers'] - mem_info['Cached']
    return mem_info

# psutil库netifaces
def get_cpu_info():
    with open('/proc/stat', 'r') as f:
        line_1 = f.readline()
        cpu_time_list = re.findall(r'\d+', line_1)
        cpu_idle1 = int(cpu_time_list[3])
        total_cpu_time1 = 0
        for t in cpu_time_list:
            total_cpu_time1 = total_cpu_time1 + int(t)
    time.sleep(1)
    with open('/proc/stat', 'r') as f_2:
        line_2 = f_2.readline()
        cpu_time_list_2 = re.findall(r'\d+', line_2)
        cpu_idle2 = int(cpu_time_list_2[3])
        total_cpu_time2 = 0
        for t in cpu_time_list_2:
            total_cpu_time2 = total_cpu_time2 + int(t)
    cpu_usage = 1 - (cpu_idle2 - cpu_idle1) / (total_cpu_time2 - total_cpu_time1)
    return {"cpu_use":cpu_usage}


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
    uptime['FreeRate'] = float(con[1]) / float(con[0])
    return uptime

# 获取网卡流量信息 /proc/net/dev
def net_stat():
    f = open("/proc/net/dev")
    lines = f.readlines()
    f.close()
    dict_intf = {}
    for line in lines[2:]:
        if 'ens33' in line:
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
            dict_intf = dict(
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
            break
 
    return dict_intf

# 磁盘空间使用
import os, sys
def disk_stat():
    hd={}
    disk = os.statvfs("/")
    hd['free'] = disk.f_bavail * disk.f_frsize
    hd['total'] = disk.f_blocks * disk.f_frsize
    hd['used'] = (disk.f_blocks - disk.f_bfree) * disk.f_frsize
    return hd

