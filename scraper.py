import requests
from datetime import datetime

# 1. 設定目標：文化部開放資料 API (展覽類別)
url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6"

print("正在連線到文化部資料庫，請稍等...")
response = requests.get(url)

if response.status_code == 200:
    print("連線成功！正在篩選「台北」且「還沒結束」的展覽...\n")
    
    # 把抓回來的資料變成 Python 看得懂的清單
    exhibitions = response.json()
    
    # 取得現在的時間 (用來比對展覽是不是過期了)
    now = datetime.now()
    
    count = 0 # 計數器：紀錄我們找到了幾筆
    
    for show in exhibitions: 
        # --- 第一關：檢查資料完不完整 ---
        # 如果沒有詳細資訊 (showInfo 是空的)，就跳過看下一筆
        if len(show['showInfo']) == 0:
            continue
            
        # 取出詳細資訊
        info = show['showInfo'][0]
        
        # --- 第二關：檢查是不是過期了 ---
        end_time_str = info.get('endTime', '') # 抓取結束時間
        
        if end_time_str == '': # 如果沒寫時間，保險起見先跳過
            continue
            
        try:
            # 把文字時間 "2025/12/31 23:59:59" 轉換成電腦的時間物件
            end_time = datetime.strptime(end_time_str, "%Y/%m/%d %H:%M:%S")
            
            # 關鍵時刻：如果「結束時間」比「現在」還早，代表過期了
            if end_time < now:
                continue # 跳過這筆 (過期)
                
        except:
            continue # 如果時間格式怪怪的，也先跳過
            
        # --- 第三關：檢查地點 (通過前兩關的倖存者才能來到這裡) ---
        title = show['title']
        location = info['location']
        time_str = info['time']
        
        # 只要地點有寫 "台北" 或 "臺北" 都算數
        if location and ("台北" in location or "臺北" in location):
            print(f"展覽：{title}")
            print(f"時間：{time_str}")
            print(f"地點：{location}")
            print("-" * 30) # 畫一條分隔線
            count += 1
            
        # 我們只印出前 10 筆，不然畫面會太長
        if count >= 10:
            break
            
    print(f"\n報告長官：篩選完畢！我們幫你找到了 {count} 筆正在進行的台北展覽！")

else:
    print("連線失敗QQ，代碼：", response.status_code)