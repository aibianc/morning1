import requests
from datetime import datetime,date
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
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

logger.info(f"当前日期和时间: {today}")
logger.info(f"开始日期: {start_date}")
logger.info(f"城市: {city}")
logger.info(f"生日: {birthday}")
logger.info(f"应用ID: {app_id}")
logger.info(f"应用密钥: {app_secret}")
logger.info(f"用户ID: {user_id}")
logger.info(f"模板ID: {template_id}")

def get_weather():
    try:
        url = f"https://devapi.qweather.com/v7/weather/3d?location={city}&key=a4317352c6e444e683112ac77c3896b8"
        res = requests.get(url)
        res.raise_for_status()
        weather_data = res.json()
        daily_weather = weather_data.get('daily', [{}])[0]
        if daily_weather:
            weather_date = daily_weather.get('fxDate', '未知')
            weather_temp_max = math.floor(float(daily_weather.get('tempMax', 0)))
            weather_temp_min = math.floor(float(daily_weather.get('tempMin', 0)))
            weather_day = daily_weather.get('textDay', '未知')
            sunset_time = daily_weather.get('sunset', '未知')
            moon_phase = daily_weather.get('moonPhase', '未知')
            uv_index = int(daily_weather.get('uvIndex', 0))
            uv_warning = ""
            umbrella_reminder = ""
            
            if uv_index > 7 and uv_index < 9:
                uv_warning = "今天紫外线稍强，请注意防晒。"
            elif uv_index >= 9:
                uv_warning = "今天紫外线很强，请外出时做好防晒措施。"

            if '雨' in weather_day:
                umbrella_reminder = "今天天气有雨，请记得携带雨伞。"

            today_weather = {
                'weather_date': weather_date,
                'weather_temp_max': weather_temp_max,
                'weather_temp_min': weather_temp_min,
                'weather_day': weather_day,
                'sunset_time': sunset_time,
                'moon_phase': moon_phase,
                'uv_index': uv_index,
                'uv_warning': uv_warning,
                'umbrella_reminder': umbrella_reminder
            }
            
            logging.info(f"Weather data: {today_weather}")
            return today_weather
        else:
            return {
                'weather_date': '未知',
                'weather_temp_max': 0,
                'weather_temp_min': 0,
                'weather_day': '未知',
                'sunset_time': '未知',
                'moon_phase': '未知',
                'uv_index': 0,
                'uv_warning': '',
                'umbrella_reminder': ''
            }
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return {
            'weather_date': '未知',
            'weather_temp_max': 0,
            'weather_temp_min': 0,
            'weather_day': '未知',
            'sunset_time': '未知',
            'moon_phase': '未知',
            'uv_index': 0,
            'uv_warning': '',
            'umbrella_reminder': ''
        }

def get_count():
    delta = today - datetime.strptime(start_date, "%Y-%m-%d")
    count = delta.days
    logging.info(f"Love days count: {count}")

    # 判断是否满足特定的纪念日条件（比如100、200、300...天）
    if count > 0 and count % 100 == 0:
        anniversary_message = f"今天我们认识满{count}天啦！"
        logging.info(f"Anniversary message: {anniversary_message}")
    else:
        anniversary_message = None

    return count, anniversary_message

def get_birthday():
    next_birthday = datetime.strptime(f"{date.today().year}-{birthday}", "%Y-%m-%d")
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=next_birthday.year + 1)
    days_left = (next_birthday - today).days

    # 判断是否为生日当天
    if days_left == 0:
        birthday_wish = "记得嘛，今天是小寿星嗷！生日快乐！"
    else:
        birthday_wish = ""
    
    logging.info(f"Days left for birthday: {days_left}")
    logging.info(f"Birthday wish: {birthday_wish}")
    
    return days_left, birthday_wish


def get_words(test_words=None):
    try:
        if test_words:
            words = test_words
        else:
            response = requests.get("https://api.xygeng.cn/one")
            response.raise_for_status()
            words = response.json()['data']['content']

        # 格式化处理每日一言，根据需要进行分割
        formatted_words = format_daily_quote(words)
        logging.info(f"Original Words: {words}")
        logging.info(f"Formatted Words: {formatted_words}")

        if len(formatted_words) > 114:
            logging.warning("Daily quote length exceeds 114 characters. Fetching a new quote.")
            response = requests.get("https://api.xygeng.cn/one")
            response.raise_for_status()
            words = response.json()['data']['content']
            formatted_words = format_daily_quote(words)

        # 分割处理
        words_parts = split_words(formatted_words)
        logging.info(f"Words Parts: {words_parts}")
        
        # 返回分割后的结果，最多返回六段
        return words_parts[:6]
    except requests.RequestException as e:
        logging.error(f"Error fetching words: {e}")
        return ["每天都要爱自己奥！"] * 6  # 返回默认值

def split_words(words):
    # 根据长度分割成最多6段，每段不超过19个中文字符
    max_length = 19
    words_parts = []
    while len(words) > max_length:
        words_parts.append(words[:max_length])
        words = words[max_length:]
    if words:
        words_parts.append(words)
    # 填充到6段
    while len(words_parts) < 6:
        words_parts.append("")
    return words_parts

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
    
    today_weather = get_weather()
    love_days, anniversary_message = get_count()  
    birthday_left, birthday_wish = get_birthday()
    words_parts = get_words()
    
    # 构建 data 字典，使用更具描述性的键名和额外的字段
    data = {
        "weather_date": {"value": today_weather['weather_date']},
        "weather_temp_max": {"value": today_weather['weather_temp_max']},
        "weather_temp_min": {"value": today_weather['weather_temp_min']},
        "weather_day": {"value": today_weather['weather_day']},
        "sunset_time": {"value": today_weather['sunset_time']},
        "moon_phase": {"value": today_weather['moon_phase']},
        "uv_index": {"value": today_weather['uv_index']},
        "uv_warning": {"value": today_weather['uv_warning']},
        "umbrella_reminder": {"value": today_weather['umbrella_reminder']},
        "love_days": {"value": love_days},
        "an_message":{"value" anniversary_message},
        "birthday_left": {"value": birthday_left},
        "birthday_wish": {"value": birthday_wish}, 
        "words1": {"value": words_parts[0]},
        "words2": {"value": words_parts[1]},
        "words3": {"value": words_parts[2]},
        "words4": {"value": words_parts[3]},
        "words5": {"value": words_parts[4]},
        "words6": {"value": words_parts[5]}
    }
    
    # 打印所有数据
    logging.info(f"Data to be sent: {data}")
    
    # 发送模板消息
    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
