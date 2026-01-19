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

# 👇 把原本的 get_exhibitions 整段換成這個
def get_exhibitions():
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"
    
    # 🎭 戴上面具：假裝我們是普通的瀏覽器，不是機器人
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 👇 修改這一行：加上 verify=False (叫 Python 不要太嚴格檢查安全憑證)
        response = requests.get(url, headers=headers, verify=False)
        exhibitions = response.json()
    except Exception as e:
        # 👇 新增這一行：如果失敗了，把真正的錯誤原因印在黑色視窗給我們看
        print("抓取失敗，錯誤原因：", e)
        return "剛睡醒腦袋運轉中... 😵‍💫 請再傳一次「看展」我就會醒來囉！"
        
    now = datetime.now()
    count = 0
    result_text = "🎨 幫你找到最新的台北展覽：\n\n"
    
    for show in exhibitions:
        if len(show['showInfo']) == 0: continue
        info = show['showInfo'][0]
        
        # 時間檢查
        end_time_str = info.get('endTime', '')
        if end_time_str == '': continue
        try:
            end_time = datetime.strptime(end_time_str, "%Y/%m/%d %H:%M:%S")
            if end_time < now: continue
        except: continue
            
        # 地點檢查
        location = info['location']
        if location and ("台北" in location or "臺北" in location):
            result_text += f"📍 {show['title']}\n"
            result_text += f"📅 {info['time']}\n"
            result_text += f"🏠 {location}\n"
            result_text += "-" * 15 + "\n"
            count += 1
            
        if count >= 5: break
        
    if count == 0:
        return "最近好像沒有展覽耶..."
        
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
    
    # 👇 新增這段：測試機器人是不是活著
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