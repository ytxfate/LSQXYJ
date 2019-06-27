from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import re
import time

ICON_URL = 'http://www.weather.com.cn/static/html/legend.shtml'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}

# request = Request(ICON_URL, headers=HEADERS)
# web_html = urlopen(request)
# bs_obj = BeautifulSoup(web_html, 'lxml')

# div_tab_leftbox = bs_obj.find("div",{"class":"tab_leftbox"})
# tables = div_tab_leftbox.findAll("table")
# list_tmp = []
# n = 0
# for table in tables:
#     ss = ""
#     if n == 0:
#         ss = "白天-"
#     else:
#          ss = "夜间-"
#     tds = table.findAll("td")
#     for td in tds:
#         a_datas = td.findAll("a")
#         if len(a_datas) >0:
#             a_data_1 = a_datas[0]
#             a_data_2 = a_datas[1]
#             reg = re.compile(r'<a.*src="(.*gif)".*</a>')
#             srcs = reg.findall(str(a_data_1))
#             dict_tmp = {
#                 "name": ss+a_data_2.string,
#                 "src": srcs[0]
#             }
#             print(dict_tmp)
#             list_tmp.append(dict_tmp)
#             dict_tmp.clear()
#             # print(len(list_tmp))
#     n += 1
#     if n == 2:
#         break
# ==========================
list_tmp = [{"name": "白天-晴", "src": "http://www.weather.com.cn/m/i/icon_weather/42x30/d00.gif"}               ,
{"name":"白天-多云","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d01.gif"},
{"name":"白天-阴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d02.gif"},
{"name":"白天-阵雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d03.gif"},
{"name":"白天-雷阵雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d04.gif"},
{"name":"白天-雷阵雨伴有冰雹","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d05.gif"},
{"name":"白天-雨夹雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d06.gif"},
{"name":"白天-小雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d07.gif"},
{"name":"白天-中雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d08.gif"},
{"name":"白天-大雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d09.gif"},
{"name":"白天-暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d10.gif"},
{"name":"白天-大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d11.gif"},
{"name":"白天-特大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d12.gif"},
{"name":"白天-阵雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d13.gif"},
{"name":"白天-小雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d14.gif"},
{"name":"白天-中雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d15.gif"},
{"name":"白天-大雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d16.gif"},
{"name":"白天-暴雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d17.gif"},
{"name":"白天-雾","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d18.gif"},
{"name":"白天-冻雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d19.gif"},
{"name":"白天-沙尘暴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d20.gif"},
{"name":"白天-小雨-中雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d21.gif"},
{"name":"白天-中雨-大雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d22.gif"},
{"name":"白天-大雨-暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d23.gif"},
{"name":"白天-暴雨-大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d24.gif"},
{"name":"白天-大暴雨-特大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d25.gif"},
{"name":"白天-小雪-中雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d26.gif"},
{"name":"白天-中雪-大雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d27.gif"},
{"name":"白天-大雪-暴雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d28.gif"},
{"name":"白天-浮尘","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d29.gif"},
{"name":"白天-扬沙","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d30.gif"},
{"name":"白天-强沙尘暴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d31.gif"},
{"name":"白天-霾","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/d53.gif"},
{"name":"夜间-晴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n00.gif"},
{"name":"夜间-多云","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n01.gif"},
{"name":"夜间-阴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n02.gif"},
{"name":"夜间-阵雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n03.gif"},
{"name":"夜间-雷阵雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n04.gif"},
{"name":"夜间-雷阵雨伴有冰雹","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n05.gif"},
{"name":"夜间-雨夹雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n06.gif"},
{"name":"夜间-小雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n07.gif"},
{"name":"夜间-中雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n08.gif"},
{"name":"夜间-大雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n09.gif"},
{"name":"夜间-暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n10.gif"},
{"name":"夜间-大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n11.gif"},
{"name":"夜间-特大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n12.gif"},
{"name":"夜间-阵雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n13.gif"},
{"name":"夜间-小雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n14.gif"},
{"name":"夜间-中雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n15.gif"},
{"name":"夜间-大雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n16.gif"},
{"name":"夜间-暴雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n17.gif"},
{"name":"夜间-雾","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n18.gif"},
{"name":"夜间-冻雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n19.gif"},
{"name":"夜间-沙尘暴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n20.gif"},
{"name":"夜间-小雨-中雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n21.gif"},
{"name":"夜间-中雨-大雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n22.gif"},
{"name":"夜间-大雨-暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n23.gif"},
{"name":"夜间-暴雨-大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n24.gif"},
{"name":"夜间-大暴雨-特大暴雨","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n25.gif"},
{"name":"夜间-小雪-中雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n26.gif"},
{"name":"夜间-中雪-大雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n27.gif"},
{"name":"夜间-大雪-暴雪","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n28.gif"},
{"name":"夜间-浮尘","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n29.gif"},
{"name":"夜间-扬沙","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n30.gif"},
{"name":"夜间-强沙尘暴","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n31.gif"},
{"name":"夜间-霾","src":"http://www.weather.com.cn/m/i/icon_weather/42x30/n53.gif"}]
for dd in list_tmp:
    try:
        f = open("icons\\"+dd["name"]+".gif", 'wb')
        time.sleep(1)
        f.write((urlopen(dd["src"])).read())
        f.close()
        print("get "+dd["name"]+".gif")
    except:
        print("get "+dd["name"]+".gif error!!!")
