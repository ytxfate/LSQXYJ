from flask import Blueprint, request, Response, send_file
import datetime
import json
from operator import itemgetter

from util import base_operate

conn_mongo, db_mongo = base_operate.get_mongodb()
conn_redis = base_operate.get_redis()

# 定义模板
search = Blueprint('search',__name__)

# 
dict_weather_code_table = {
    "d00":"白天-晴",
    "d01":"白天-多云",
    "d02":"白天-阴",
    "d03":"白天-阵雨",
    "d04":"白天-雷阵雨",
    "d05":"白天-雷阵雨伴有冰雹",
    "d06":"白天-雨夹雪",
    "d07":"白天-小雨",
    "d08":"白天-中雨",
    "d09":"白天-大雨",
    "d10":"白天-暴雨",
    "d11":"白天-大暴雨",
    "d12":"白天-特大暴雨",
    "d13":"白天-阵雪",
    "d14":"白天-小雪",
    "d15":"白天-中雪",
    "d16":"白天-大雪",
    "d17":"白天-暴雪",
    "d18":"白天-雾",
    "d19":"白天-冻雨",
    "d20":"白天-沙尘暴",
    "d21":"白天-小雨-中雨",
    "d22":"白天-中雨-大雨",
    "d23":"白天-大雨-暴雨",
    "d24":"白天-暴雨-大暴雨",
    "d25":"白天-大暴雨-特大暴雨",
    "d26":"白天-小雪-中雪",
    "d27":"白天-中雪-大雪",
    "d28":"白天-大雪-暴雪",
    "d29":"白天-浮尘",
    "d30":"白天-扬沙",
    "d31":"白天-强沙尘暴",
    "d53":"白天-霾"
}
# map 页面
@search.route('/get_area_weather_info', methods=['GET'])
def get_regulatory_anomaly():
    area = request.args.get('area')
    collection = db_mongo.get_collection('seven_days_weather')
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    now_date_hour = datetime.datetime.now().strftime('%Y%m%d%H')
    # print(now_date_hour)
    # now_date_time = now_date[:13].replace('-','').replace(' ','')
    list_end = []
    rows = []
    # ================== 测试使用 ================== #
    now_date = '2019-04-07'
    now_date_hour = '2019040712'
    # ============================================= #
    if area == '凉山州':
        # rows = collection.find({"area":"county", "date":now_date[:10]},{'_id':0})
        rows = collection.find({"area":"county", "date":now_date},{'_id':0})
    else:
        rows = collection.find({"county":area[:2], "date":now_date},{'_id':0})
    
    for row in rows:
        data_sta = False
        if 'weather_info' in row and row['name'] != '城区':
            list_weather_seven = row['weather_info']
            father = ''
            if 'county' in row:
                father = row['county']
            for weather_seven in list_weather_seven:
                for weather in weather_seven:
                    if 'date_hour' in weather:
                        if weather['date_hour'] == now_date_hour:
                            weather_name = dict_weather_code_table['d'+weather['weather_code']]
                            dict_tmp = {
                                'area': row['name'],
                                'father': father,
                                'weather': weather_name
                            }
                            data_sta = True
                            list_end.append(dict_tmp)
                    if data_sta:
                        break
                if data_sta:
                    break
    return Response(json.dumps(list_end,ensure_ascii=False), mimetype='application/json')


# 详情页面
@search.route('/get_detail_weather_info', methods=['GET'])
def get_detail_weather_info():
    area = request.args.get('area')
    county = request.args.get('county')
    dict_tmp = {}
    if area:
        dict_tmp['name'] = area
    if county:
        dict_tmp['county'] = county
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    now_date_str = datetime.datetime.now().strftime('%Y%m%d')
    # ================== 测试使用 ================== #
    now_date = '2019-04-07'
    now_date_str = '20190407'
    # ============================================= #
    dict_tmp['date'] = now_date
    collection = db_mongo.get_collection('seven_days_weather')
    row = collection.find_one(dict_tmp, {'_id':0})
    list_tmp = []
    if row:
        weather_infos = row['weather_info']
        for weather_info in weather_infos:
            weather = weather_info[0]
            if now_date_str in weather['date_hour']:
                list_tmp = weather_info
    list_end = []
    for l in list_tmp:
        l['weather_name'] =  dict_weather_code_table['d'+l['weather_code']]
        list_end.append(l)
    # 排序
    list_end = sorted(list_end, key=itemgetter('date_hour'))
    return Response(json.dumps(list_end,ensure_ascii=False), mimetype='application/json')
    
# 图表
@search.route('get_weather_table', methods=['GET'])
def get_weather_table():
    area = request.args.get('area')
    county = request.args.get('county')
    dict_tmp = {}
    if area:
        dict_tmp['name'] = area
    if county:
        dict_tmp['county'] = county
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # ================== 测试使用 ================== #
    now_date = '2019-04-07'
    # ============================================= #
    dict_tmp['date'] = now_date
    collection = db_mongo.get_collection('tf_hours_weather')
    row = collection.find_one(dict_tmp, {'_id':0})
    hour = []
    humidity = []
    rain = []
    temperature = []
    wind_direction = []
    wind_power = []
    if row:
        hours_info = row['hours_info']
        # hours_info = sorted(hours_info, key=itemgetter('hour'))
        for h in hours_info:
            hour.append(h['hour'])
            humidity.append(h['humidity'])
            rain.append(h['rain'])
            temperature.append(h['temperature'])
            wind_direction.append(h['wind_direction'])
            wind_power.append(h['wind_power'])
    dict_tmp = {}
    if hour:
        dict_tmp['hour'] = hour
    if humidity:
        dict_tmp['humidity'] = humidity
    if rain:
        dict_tmp['rain'] = rain
    if temperature:
        dict_tmp['temperature'] = temperature
    if hour:
        dict_tmp['wind_direction'] = wind_direction
    if hour:
        dict_tmp['wind_power'] = wind_power
    return Response(json.dumps(dict_tmp,ensure_ascii=False), mimetype='application/json')

# 生活助手
@search.route('/get_life_weather_info', methods=['GET'])
def get_life_weather_info():
    area = request.args.get('area')
    county = request.args.get('county')
    dict_tmp = {}
    if area:
        dict_tmp['name'] = area
    if county:
        dict_tmp['county'] = county
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # ================== 测试使用 ================== #
    now_date = '2019-04-07'
    # ============================================= #
    dict_tmp['date'] = now_date
    collection = db_mongo.get_collection('life_weather')
    row = collection.find_one(dict_tmp, {'_id':0})
    list_end = []
    if row:
        list_end = row['life_info']
    return Response(json.dumps(list_end,ensure_ascii=False), mimetype='application/json')

# 未来七天
@search.route('/get_seven_day_weather', methods=['GET'])
def get_seven_day_weather():
    area = request.args.get('area')
    county = request.args.get('county')
    dict_tmp = {}
    if area:
        dict_tmp['name'] = area
    if county:
        dict_tmp['county'] = county
    now_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # ================== 测试使用 ================== #
    now_date = '2019-04-07'
    # ============================================= #
    dict_tmp['date'] = now_date
    collection = db_mongo.get_collection('seven_days_weather')
    row = collection.find_one(dict_tmp, {'_id':0})
    list_end = []
    list_e = []
    if row:
        weather_infos = row['weather_info']
        for weather_info in weather_infos:
            for weather in weather_info:
                if weather['date_hour'][-2:] == '14':
                    list_e.append(weather)
                    break
    for l in list_e:
        l['weather_name'] = dict_weather_code_table['d'+l['weather_code']]
        list_end.append(l)
    if list_end:
        list_end = sorted(list_end, key=itemgetter('date_hour'))
    return Response(json.dumps(list_end,ensure_ascii=False), mimetype='application/json')

# 预警信息
@search.route('/get_warning_weather', methods=['GET'])
def get_warning_weather():
    now_date = datetime.datetime.now().strftime('%Y%m%d')
    # ================== 测试使用 ================== #
    now_date = '20190310'
    # ============================================= #
    collection = db_mongo.get_collection('warning_weather')
    row = collection.find_one({'AlermInfo.dt': now_date}, {'_id':0})
    list_end = []
    if row and 'AlermInfo' in row:
        AlermInfo = row['AlermInfo']
        dict_code = {
            '蓝色': 'b',
            '红色': 'r',
            '橙色': 'o',
            '黄色': 'y'
        }
        for key, value in AlermInfo.items():
            if key == 'dt' or key == 'hourType' or key == 'other':
                continue
            elif 'Station' in value and value['Station']:
                for warin_info in value['Station']:
                    dict_t = {
                        'stationName': warin_info['stationName'],
                        'signalLevel': warin_info['signalLevel'],
                        'img_url': key + '_' + dict_code[warin_info['signalLevel']] + '.jpg',
                        'issueContent': warin_info['issueContent'],
                        'signalType': warin_info['signalType'],
                        'jd': warin_info['lon'],
                        'wd': warin_info['lat']
                    }
                    list_end.append(dict_t)
    if list_end:
        return Response(json.dumps(list_end,ensure_ascii=False), mimetype='application/json')
    else:
        return Response(json.dumps([],ensure_ascii=False), mimetype='application/json')