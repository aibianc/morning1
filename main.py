from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import requests
import os
import logging
import re

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


def get_words(test_words=None):
    try:
        if test_words:
            words = test_words
        else:
            response = requests.get("https://api.xygeng.cn/one")
            response.raise_for_status()
            words = response.json()['data']['content']
        
        formatted_words = format_daily_quote(words)
        logging.info(f"Formatted Words: {formatted_words}")
        return formatted_words
    except requests.RequestException as e:
        logging.error(f"Error fetching words: {e}")
        return "每天都要爱自己奥！"




def format_daily_quote(text):
    # 分割文本为句子
    sentences = re.split(r'(?<=[。！？\n])', text)
    
    # 处理每个句子
    formatted_sentences = []
    for sentence in sentences:
        if not sentence:
            continue
        # 去掉句子前后的空白字符
        sentence = sentence.strip()
        
        # 如果句子末尾不是标点符号，则添加句号
        if sentence and sentence[-1] not in '。！？…':
            sentence += '。'
        
        # 如果句子包含换行符且不以逗号结尾，则将换行符替换为逗号
        if '\n' in sentence and not sentence.endswith('，'):
            sentence = sentence.replace('\n', '，')
        # 如果句子包含换行符且以逗号结尾，则删除换行符
        elif '\n' in sentence and sentence.endswith('，'):
            sentence = sentence.replace('\n', '')

        # 添加到结果列表
        formatted_sentences.append(sentence)
    
    # 将处理后的句子合并为一个字符串
    formatted_text = ''.join(formatted_sentences)
    return formatted_text

try:
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)
    
    weather, temperature = get_weather()
    love_days = get_count()
    birthday_left = get_birthday()
    words = get_words(只佩服张幼仪，不容易，尽管从小接受的是封建教育，还被渣男抛弃，一个孕妇在外国没钱没人脉，最后却自立自强，忍受偏见，成为一个女强人。可怜念了徐志摩一辈子，世人都在赞颂康桥故事，不过是渣男精神出轨的一幕而已[大笑])
    
    data = {
        "weather": {"value": weather},
        "temperature": {"value": temperature},
        "love_days": {"value": love_days},
        "birthday_left": {"value": birthday_left},
        "words": {"value": words}
    }
    
    # 打印所有数据
    logging.info(f"Data to be sent: {data}")
    
    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
