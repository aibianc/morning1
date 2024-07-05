import requests
import logging
import os

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
        str: 获取的内容.
    """
    max_attempts = 5
    for _ in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
    
    logging.error(f"Failed to fetch data from {url} after {max_attempts} attempts.")
    return None

def split_text(text, max_length):
    """
    将文本按最大长度分割成多段。
    
    Args:
        text (str): 需要分割的文本.
        max_length (int): 每段最大长度.
    
    Returns:
        list: 分割后的文本段落列表.
    """
    parts = []
    while len(text) > max_length:
        parts.append(text[:max_length])
        text = text[max_length:]
    if text:
        parts.append(text)
    return parts

try:
    # 获取微语
    weiyu_url = "https://api.vvhan.com/api/60s"
    weiyu_data = fetch_content(weiyu_url)
    if weiyu_data and weiyu_data.get('success', False):
        weiyu_list = weiyu_data.get('data', [])
        weiyu = None
        for item in weiyu_list:
            if item.startswith("【微语】"):
                weiyu = item[5:]  # 去掉"【微语】"
                break
        
        if weiyu:
            # 分割微语
            weiyu1, weiyu2, weiyu3 = weiyu[:20], weiyu[20:40], weiyu[60:]
        else:
            logging.warning("No suitable 微语 found.")
    
    # 获取诗词
    shici_url = "https://api.vvhan.com/api/ian/shici"
    shici_data = fetch_content(shici_url)
    if shici_data and shici_data.get('success', False):
        shici_list = shici_data.get('data', [])
        shici1 = shici2 = None
        for i, shici in enumerate(shici_list):
            if i == 0:
                shici1 = shici[:40] if len(shici) > 40 else shici
            elif i == 1:
                shici2 = shici[:40] if len(shici) > 40 else shici
            else:
                break
    
    # 获取摸鱼人日历
    moyu_url = "https://api.vvhan.com/api/moyu?type=json"
    moyu_data = fetch_content(moyu_url)
    img1 = img2 = None
    if moyu_data and moyu_data.get('success', False):
        img_url = moyu_data.get('url', '')
        if img_url:
            img1 = img_url
    
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
        "img1": {"value": img1},
        "img2": {"value": img2},
        "en": {"value": en},
        "cn": {"value": cn}
    }

    logging.info(f"Data to be sent: {data}")

    response = wm.send_template(user_id, template_id, data)
    logging.info(f"Message sent successfully: {response}")

except Exception as e:
    logging.error(f"An error occurred: {e}")
