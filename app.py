import os
import json
from datetime import datetime
import requests
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)


line_bot_api = LineBotApi('H5Id19fzUIEJD+W77RDxScqdyRuPWuz1JBblqWTyjnJtCOSvW1Zl7wdi1UbwEKY/dQqCj/1K4u3tKXS2GMkx/4fkG6O0hS46XRaYwb2ybovSxQXs3rXg+4AKt8CeaGTqthCjvNWGDE6/qgBvkzqxiwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('75806eeda75c04e912aa27470eaad174')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    
    if "看展" in user_msg:
        reply_text = get_exhibitions()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=user_msg)
        )

# 抓取展覽資料的函式
def get_exhibitions():
    try:
        # 真實的文化部網址
        url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
        
        # 偽裝面具
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 發送請求 (設定 5 秒逾時)
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        
        # 嘗試解讀資料
        exhibitions = response.json()
        
    except Exception as e:
        print("抓取失敗，錯誤原因：", e)
        return "😵‍💫 連線發生錯誤 (可能是文化部網站還沒修好，或是有連線限制) 😭"

    # 整理資料
    result_text = "🎉 幫你找到最新的台北展覽：\n\n"
    
    count = 0
    for show in exhibitions:
        # 只抓台北
        if "台北" not in show['showInfo'][0]['location']:
            continue
            
        title = show['title']
        date = show['showInfo'][0]['time']
        location = show['showInfo'][0]['locationName']
        
        result_text += f"📍 {title}\n📅 {date}\n🏢 {location}\n\n"
        
        count += 1
        if count >= 5: 
            break
            
    if count == 0:
        return "最近台北好像沒有展覽資料耶 🤔"
        
    return result_text

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)