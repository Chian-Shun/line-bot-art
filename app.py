import requests
from datetime import datetime
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import requests
from datetime import datetime
import os

app = Flask(__name__)

# ================= 鑰匙區 (請把你的密碼貼回來) =================
CHANNEL_ACCESS_TOKEN = "H5Id19fzUIEJD+W77RDxScqdyRuPWuz1JBblqWTyjnJtCOSvW1Zl7wdi1UbwEKY/dQqCj/1K4u3tKXS2GMkx/4fkG6O0hS46XRaYwb2ybovSxQXs3rXg+4AKt8CeaGTqthCjvNWGDE6/qgBvkzqxiwdB04t89/1O/w1cDnyilFU=n"
CHANNEL_SECRET = "75806eeda75c04e912aa27470eaad174"
# ==========================================================

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


def get_exhibitions():
    try:
        # 👇 這是文化部的網址 (不用改)
        url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
        
        # 👇【新增】戴上「我是 Google Chrome 瀏覽器」的面具
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # 👇 請求時戴上面具 (headers) 並關閉安全檢查 (verify=False)
        response = requests.get(url, headers=headers, verify=False)
        
        # 試著解讀資料
        exhibitions = response.json()
        
    except Exception as e:
        # 如果還是失敗，把錯誤印出來
        print("抓取失敗，錯誤原因：", e)
        return "😭 嗚嗚... 連不上文化部 QQ"

    # 👇 如果成功拿到資料，就開始整理 (這段跟原本一樣)
    now = datetime.now()
    result_text = "🎉 幫你找到最新的台北展覽：\n\n"
    
    count = 0
    for show in exhibitions:
        # 只抓台北的展覽
        if "台北" not in show['showInfo'][0]['location']:
            continue
            
        # 整理展覽資訊
        title = show['title']
        date = show['showInfo'][0]['time']
        location = show['showInfo'][0]['locationName']
        
        result_text += f"📍 {title}\n📅 {date}\n🏢 {location}\n\n"
        
        count += 1
        if count >= 5: # 只回傳前 5 個
            break
            
    if count == 0:
        return "最近台北好像沒有展覽資料耶 🤔"
        
    return result_text

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'
 

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text # 使用者傳來的文字
    
    # 測試機器人是不是活著
    if user_msg == "嗨":
        return "你好！我現在住在美國的雲端主機上喔！☁️🇺🇸"
    # 判斷使用者是不是想看展
    if "看展" in user_msg or "展覽" in user_msg:
        reply_msg = get_exhibitions() # 呼叫爬蟲功能！
    else:
        reply_msg = "你想看展覽嗎？試試看輸入「看展」這兩個字，我就會幫你找喔！"

    # 回覆訊息
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_msg)]
            )
        )

if __name__ == "__main__":
    app.run(port=5001)