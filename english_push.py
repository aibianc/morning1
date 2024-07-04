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

def fetch_daily_english():
    """
    从API获取每日英语和中文句子。
    
    Returns:
        english_sentence (str): 英文句子.
        chinese_sentence (str): 中文句子.
    """
    max_english_length = 120
    max_chinese_length = 40
    
    try:
        api_url = "https://api.vvhan.com/api/dailyEnglish?type=sj"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json().get('data', {})
        english_sentence = data.get('en', '')
        chinese_sentence = data.get('zh', '')

        # 检查英文句子长度
        if len(english_sentence) > max_english_length:
            logging.warning("English sentence exceeds maximum length.")
            return None, None
        
        # 检查中文句子长度
        if len(chinese_sentence) > max_chinese_length:
            logging.warning("Chinese sentence exceeds maximum length.")
            return None, None
        
        return english_sentence, chinese_sentence
    
    except requests.RequestException as e:
        logging.error(f"Error fetching daily English: {e}")
        return None, None

def split_text(text, max_length):
    """
    将文本按最大长度分割成多段。
    
    Args:
        text (str): 需要分割的文本.
        max_length (int): 每段最大长度.
    
    Returns:
        parts (list): 分割后的文本段落列表.
    """
    parts = []
    while len(text) > max_length:
        parts.append(text[:max_length])
        text = text[max_length:]
    if text:
        parts.append(text)
    return parts

def format_data(english_sentences, chinese_sentences):
    """
    格式化英文和中文句子，按照要求存储到words列表中。
    
    Args:
        english_sentences (list): 英文句子列表，包含5个句子.
        chinese_sentences (list): 中文句子列表，包含5个句子.
    
    Returns:
        words (list): 格式化后的句子列表，长度为20.
    """
    words = [""] * 20
    
    # 存储句子到指定位置
    index_mapping = [
        (0, 1),  # 第一次请求的英文存到words1和words2
        (2, 3),  # 第一次请求的中文存到words3和words4
        (4, 5),  # 第二次请求的英文存到words5和words6
        (6, 7),  # 第二次请求的中文存到words7和words8
        (8, 9),  # 第三次请求的英文存到words9和words10
        (10, 11), # 第三次请求的中文存到words11和words12
        (12, 13), # 第四次请求的英文存到words13和words14
        (14, 15), # 第四次请求的中文存到words15和words16
        (16, 17), # 第五次请求的英文存到words17和words18
        (18, 19)  # 第五次请求的中文存到words19和words20
    ]

    for i, (eng_index, chi_index) in enumerate(index_mapping):
        if i < len(english_sentences) and english_sentences[i]:
            english_parts = split_text(english_sentences[i], 60)
            for j, part in enumerate(english_parts):
                if eng_index + j < len(words):
                    words[eng_index + j] = part

        if i < len(chinese_sentences) and chinese_sentences[i]:
            chinese_parts = split_text(chinese_sentences[i], 20)
            for j, part in enumerate(chinese_parts):
                if chi_index + j < len(words):
                    words[chi_index + j] = part

    return words

try:
    # 获取每日英语和中文句子
    english_sentences = []
    chinese_sentences = []

    retries = 5
    for _ in range(retries):
        english_sentence, chinese_sentence = fetch_daily_english()
        if english_sentence and chinese_sentence:
            english_sentences.append(english_sentence)
            chinese_sentences.append(chinese_sentence)
        if len(english_sentences) >= 5 and len(chinese_sentences) >= 5:
            break

    if len(english_sentences) >= 5 and len(chinese_sentences) >= 5:
        # 格式化句子并构建data字典
        words = format_data(english_sentences, chinese_sentences)
        data = {}
        
        # 组装data字典
        for i in range(20):
            data[f"words{i + 1}"] = {"value": words[i]}

        logging.info(f"Data to be sent: {data}")
        
        # 初始化微信客户端和消息对象
        client = WeChatClient(app_id, app_secret)
        wm = WeChatMessage(client)

        # 发送模板消息
        response = wm.send_template(user_id, template_id, data)
        logging.info(f"Message sent successfully: {response}")
    else:
        logging.warning("Failed to fetch enough daily English and Chinese sentences.")
except Exception as e:
    logging.error(f"An error occurred: {e}")
