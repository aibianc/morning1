import requests
import logging
import os
import random

from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 从环境变量中获取配置信息
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]

logging.info(f"应用ID: {app_id}")
logging.info(f"应用密钥: {app_secret}")
logging.info(f"用户ID: {user_id}")
logging.info(f"模板ID: {template_id}")

def fetch_content(url):
    """
    从指定的API获取内容并返回。
    
    Args:
        url (str): API的URL.
        
    Returns:
        dict: 获取的内容的JSON格式，如果请求失败则返回None。
    """
    max_attempts = 3  # 最大重试次数
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt}: Error fetching data from {url}: {e}")
    
    logging.error(f"Failed to fetch data from {url} after {max_attempts} attempts.")
    return None

try:
    # 获取微语
    

    # 定义情话字典
    love_quotes = {
        1: "小杨，因为有你，生活多才了一份甜蜜。",
        2: "遇见小杨，是我今生最美的风景。",
        3: "宝宝，无论天涯海角，我的心永远与你相随。",
        4: "喜欢小杨，就像春风吹过心田，无法停止。",
        5: "小杨，每一次心跳都在为你而跳动。",
        6: "因为有你--宝宝，黑夜也变得温暖。",
        7: "和你在一起的时光是我最珍贵的回忆。",
        8: "世界上最幸福的事，就是遇见了你，宝宝。",
        9: "想牵小杨的手，直到岁月的尽头。",
        10: "宝宝，你是我心底最温柔的秘密。",
        11: "小杨，在你眼中，我看到了整个世界。",
        12: "杨，只要有你在，生活就充满了阳光。",
        13: "杨，爱上你，是我人生中最正确的选择。",
        14: "宝宝，你的微笑，是我最想守护的风景。",
        15: "小杨今天也要记得开心喔！",
    }

    # 随机获取一条情话
    weiyu = random.choice(list(love_quotes.values()))

    # 如果情话超过60字符，替换为默认值
    if len(weiyu) > 60:
        weiyu = "早安"

    # 分割微语
    weiyu1, weiyu2, weiyu3 = weiyu[:20], weiyu[20:40], weiyu[40:] if len(weiyu) > 40 else ""



    # 获取诗句
    shici_url = "https://v2.alapi.cn/api/shici?type=all&token=LwExDtUWhF3rH5ib"
    shici_data = fetch_content(shici_url)
    if shici_data and shici_data.get('success', False):
        shici_content = shici_data.get('data', {}).get('content', '')
        if len(shici_content) > 40:
            # 重新获取诗句
            shici_data = fetch_content(shici_url)
            if shici_data and shici_data.get('success', False):
                shici_content = shici_data.get('data', {}).get('content', '')
            else:
                shici_content = "今天没搜到诗词喔，下次再尝试！"
                if len(shici_content) > 40:
                    shici1 = shici_content[:20]
                    shici2 = shici_content[20:]
                else:
                    shici1 = shici_content[:20]
                    shici2 = ""
        else:
            shici1 = shici_content[:20]
            shici2 = shici_content[20:] if len(shici_content) > 20 else ""
    
    
    # 获取每日英语
    english_url = "https://api.vvhan.com/api/dailyEnglish?type=sj"
    english_data = fetch_content(english_url)
    en = cn = None
    if english_data and english_data.get('success', False):
        en = english_data['data'].get('en', '')
        cn = english_data['data'].get('zh', '')
        
        # 检查英文和中文长度，超过指定长度重新获取
        if len(en) > 60 or len(cn) > 20:
            english_data = fetch_content(english_url)
            if english_data and english_data.get('success', False):
                en = english_data['data'].get('en', '')
                cn = english_data['data'].get('zh', '')

    # 初始化微信客户端和消息对象
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    # 发送模板消息
    data = {
        "weiyu1": {"value": weiyu1},
        "weiyu2": {"value": weiyu2},
        "weiyu3": {"value": weiyu3},
        "shici1": {"value": shici1},
        "shici2": {"value": shici2},
        "en": {"value": en},
        "cn": {"value": cn}
    }

    logging.info(f"Data to be sent: {data}")

    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")

except Exception as e:
    logging.error(f"An error occurred: {e}")
