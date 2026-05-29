from flask import Flask, request
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from google.oauth2.service_account import Credentials
import gspread
import os

app = Flask(__name__)

# LINE
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(CHANNEL_SECRET)

# Google Sheet
SHEET_ID = "1uFO2slAlnIqQ83iBcPCUcZ6OakMtlaE8AuKhphPzWsk"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "google-credentials.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

# 改成你的工作表名稱
sheet = gc.open_by_key(SHEET_ID).worksheet("房東出租")


@app.route("/")
def home():
    return "LINE Bot Running"


@app.route("/callback", methods=["POST"])
def callback():

    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    print("================================")
    print("WEBHOOK HIT")
    print(body)
    print("================================")

    handler.handle(body, signature)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_text = event.message.text.strip()

    try:

       data = sheet.get_all_records()

print("==========")
print(data[:5])
print("==========")
        result = []

        for row in data:

            area = str(row.get("行政區", ""))

            if user_text in area:

                result.append(
                    f"🏠 {row.get('標題','')}\n"
                    f"📍 {row.get('行政區','')}\n"
                    f"💰 {row.get('租金','')}\n"
                    f"🔗 {row.get('網址','')}"
                )

        if result:
            reply_text = "\n\n".join(result[:5])
        else:
            reply_text = f"找不到 {user_text} 的案件"

    except Exception as e:

        print("查詢錯誤：", e)
        reply_text = "查詢失敗"

    with ApiClient(configuration) as api_client:

        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=reply_text
                    )
                ]
            )
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
