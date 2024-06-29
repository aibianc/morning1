from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import random
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

def get_weather():
    try:
        url = f"http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city={city}"
        res = requests.get(url)
        res.raise_for_status()
        weather = res.json()['data']['list'][0]
        return weather['weather'], math.floor(weather['temp'])
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return "未知", 0

def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    return delta.days

def get_birthday():
    next_birthday = datetime.strptime(f"{date.today().year}-{birthday}", "%Y-%m-%d")
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    return (next_birthday - today).days

def get_words():
    try:
        response = requests.get("https://api.xygeng.cn/one")
        response.raise_for_status()
        return response.json()['data']['content']
    except requests.RequestException as e:
        logging.error(f"Error fetching words: {e}")
        return "每天都要爱自己奥！"

def get_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

try:
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    
    weather, temperature = get_weather()
    data = {
        "weather": {"value": weather, "color": get_random_color()},
        "temperature": {"value": temperature, "color": get_random_color()},
        "love_days": {"value": get_count(), "color": get_random_color()},
        "birthday_left": {"value": get_birthday(), "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()}
    }
    
    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
