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
        dict: 获取的内容的JSON格式，如果请求失败则返回None。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

try:
    # 获取微语
    weiyu_url = "https://api.vvhan.com/api/60s"
    weiyu_data = fetch_content(weiyu_url)
    if weiyu_data and weiyu_data.get('success', False):
        weiyu_list = weiyu_data.get('data', [])
        weiyu = None
        for item in weiyu_list:
            if item.startswith("【微语】"):
               weiyu = item[5:]
                break
        
        if weiyu:
            if len(weiyu) > 60:
                weiyu = "早安"
            # 分割微语
            weiyu1, weiyu2, weiyu3 = weiyu[:20], weiyu[20:40], weiyu[40:] if len(weiyu) > 40 else ""
        else:
            logging.warning("No suitable 微语 found.")
    
    # 获取诗句
    shici_url = "https://api.vvhan.com/api/ian/shici?type=json"
    shici_data = fetch_content(shici_url)
    if shici_data and shici_data.get('success', False):
        shici_content = shici_data.get('data', {}).get('content', '')
        if len(shici_content) > 40:
            # 重新获取诗句
            shici_data = fetch_content(shici_url)
            if shici_data and shici_data.get('success', False):
                shici_content = shici_data.get('data', {}).get('content', '')
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
