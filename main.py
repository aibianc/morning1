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
        logging.info(f"Weather: {weather['weather']}, Temperature: {weather['temp']}")
        return weather['weather'], math.floor(weather['temp'])
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return "未知", 0

def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    count = delta.days
    logging.info(f"Love days count: {count}")
    return count

def get_birthday():
    next_birthday = datetime.strptime(f"{date.today().year}-{birthday}", "%Y-%m-%d")
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    days_left = (next_birthday - today).days
    logging.info(f"Days left for birthday: {days_left}")
    return days_left

def get_words():
    try:
        response = requests.get("https://api.xygeng.cn/one")
        response.raise_for_status()
        words = response.json()['data']['content']
        logging.info(f"Words: {words}")
        return words
    except requests.RequestException as e:
        logging.error(f"Error fetching words: {e}")
        return "每天都要爱自己奥！"

def get_random_color():
    color = f"#{random.randint(0, 0xFFFFFF):06x}"
    logging.info(f"Generated color: {color}")
    return color

try:
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    
    weather, temperature = get_weather()
    love_days = get_count()
    birthday_left = get_birthday()
    words = get_words()
    
    data = {
        "weather": {"value": weather, "color": get_random_color()},
        "temperature": {"value": temperature, "color": get_random_color()},
        "love_days": {"value": love_days, "color": get_random_color()},
        "birthday_left": {"value": birthday_left, "color": get_random_color()},
        "words": {"value": words, "color": get_random_color()}
    }
    
    # 打印所有数据
    logging.info(f"Data to be sent: {data}")
    
    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
