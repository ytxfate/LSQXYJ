import datetime

from base_operate import get_mongodb
import html_temp_str
from send_email import TimedSendEmail

conn_mongo, db_mongo = get_mongodb()

dict_weather_code_table = {
    "00":"晴",
    "01":"多云",
    "02":"阴",
    "03":"阵雨",
    "04":"雷阵雨",
    "05":"雷阵雨伴有冰雹",
    "06":"雨夹雪",
    "07":"小雨",
    "08":"中雨",
    "09":"大雨",
    "10":"暴雨",
    "11":"大暴雨",
    "12":"特大暴雨",
    "13":"阵雪",
    "14":"小雪",
    "15":"中雪",
    "16":"大雪",
    "17":"暴雪",
    "18":"雾",
    "19":"冻雨",
    "20":"沙尘暴",
    "21":"小雨-中雨",
    "22":"中雨-大雨",
    "23":"大雨-暴雨",
    "24":"暴雨-大暴雨",
    "25":"大暴雨-特大暴雨",
    "26":"小雪-中雪",
    "27":"中雪-大雪",
    "28":"大雪-暴雪",
    "29":"浮尘",
    "30":"扬沙",
    "31":"强沙尘暴",
    "53":"霾"
}

def get_all_need_send_email():
    """
    获取需要定时发送Email的相关信息
    """
    rows = db_mongo.get_collection('sub_weather').aggregate([
        {'$group': {
            '_id': '$username',
            'palce': {'$push': {'name':'$sub_addr_township','county':'$sub_addr_county'}}
        }}
    ])
    for row in rows:
        if row and '_id' in row:
            row['email'] = row['_id']
            del row['_id']
            yield row

def get_user_need_weather_info(places, today):
    """
    获取用户所需的所有地区的天气信息
    """
    ret_dict = {}
    for place in places:
        place['date'] = today
        ret_tmp = {}
        # 获取当天天气信息
        seven_days_weather = db_mongo.get_collection('seven_days_weather').find_one(place, {'_id':0,'weather_info':1})
        today_tmp = today.replace('-', '')
        weather_infos = []
        if seven_days_weather and 'weather_info' in seven_days_weather:
            weather_infos = seven_days_weather['weather_info']
        for weather_info in weather_infos:
            if len(weather_info) > 0 and today_tmp in weather_info[0]['date_hour']:
                ret_tmp['weather'] = weather_info
                break
        # 获取生活助手信息
        life_weather = db_mongo.get_collection('life_weather').find_one(place, {'_id':0,'life_info':1})
        life_infos = []
        if life_weather and 'life_info' in life_weather:
            life_infos = life_weather['life_info']
        ret_tmp['life'] = life_infos
        # 组装
        ret_dict[place['county'] + '-' + place['name']] = ret_tmp
    return ret_dict

def create_weather_html(ret_dict):
    """
    生成 html 模板
    """
    ret_html = html_temp_str.html_tmp_str_header
    # 组装
    # ================================= #
    for key,value in ret_dict.items():
        ret_html += '''
        <div class="place">
        '''
        html_tmp_1 = ''
        html_tmp_2 = ''
        html_tmp_3 = ''
        for ke, val in value.items():
            # 天气
            if ke == 'weather':
                html_tmp_1 = '<div class="div_weather"><table><caption>{where}</caption><tr style="background: #999"><th>时间</th>'.format(where=key)
                html_tmp_2 = '<tr style="background: #BBB"><th>天气</th>'
                html_tmp_3 = '<tr style="background: #DDD"><th>气温（°C）</th>'
                for v in val:
                    if v['date_hour'][-2:] > '07':
                        html_tmp_1 += '<td>{show_val}</td>'.format(show_val=v['date_hour'][-2:])
                        html_tmp_2 += '<td>{show_val}</td>'.format(show_val=dict_weather_code_table[v['weather_code']])
                        html_tmp_3 += '<td>{show_val}</td>'.format(show_val=v['temperature'])
                html_tmp_1 += '</tr>'
                html_tmp_2 += '</tr>'
                html_tmp_3 += '</tr></table></div>'
            # 生活助手
            elif ke == 'life':
                html_tmp_1 = '<div class="div_life"><table><tr style="background: #999">'
                html_tmp_2 = '<tr style="background: #BBB">'
                html_tmp_3 = '<tr style="background: #DDD">'
                for v in val:
                    html_tmp_1 += '<th>{show_val}</th>'.format(show_val=v['a'])
                    html_tmp_2 += '<td>{show_val}</td>'.format(show_val=v['b'])
                    html_tmp_3 += '<td>{show_val}</td>'.format(show_val=v['c'])
                html_tmp_1 += '</tr>'
                html_tmp_2 += '</tr>'
                html_tmp_3 += '</tr></table></div></div>'

            ret_html += html_tmp_1 + html_tmp_2 + html_tmp_3
    # ================================= #
    ret_html += html_temp_str.html_tmp_str_footer
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(ret_html)
    return ret_html

def main_func():
    "定时发送"
    # 当天日期
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    tse = TimedSendEmail()
    # ================================= #
    # 测试使用
    today = '2019-04-07'
    # ================================= #
    infos = get_all_need_send_email()
    for info in infos:
        if 'email' in info and 'palce' in info:
            ret_dict = get_user_need_weather_info(info['palce'], today)
            # 生成 html
            if ret_dict:
                ret_html = create_weather_html(ret_dict)
                if ret_html:
                    # 发送邮件
                    tse.send_eamil(info['email'], '凉山气象预报预警系统-天气订阅信息', ret_html)
                    print(info['email'] + ' send weather email ending.')

# if __name__ == "__main__":
#     main_func()

# 定时执行
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()
sched.add_job(main_func, 'cron', hour=8, minute = 40,second = 1)
sched.start()