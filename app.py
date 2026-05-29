from flask import Flask, request
import os
import gspread

from google.oauth2.service_account import Credentials

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

app = Flask(__name__)

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "/etc/secrets/google-credentials.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

configuration = Configuration(
    access_token=LINE_CHANNEL_ACCESS_TOKEN
)


@app.route("/")
def home():
    return "LINE Bot Running"


@app.route("/callback", methods=["POST"])
def callback():

    body = request.get_json()

    try:

        events = body.get("events", [])

        for event in events:

            if event.get("type") != "message":
                continue

            text = event["message"]["text"]
            reply_token = event["replyToken"]

            message_text = "查無資料"

            # 找區域
            if text.startswith("找 "):

                area = text.replace("找 ", "").strip()

                sheet = gc.open_by_key(SHEET_ID).worksheet("出租案件")

                rows = sheet.get_all_records()

                result = []

                for row in rows:

                    if area in str(row["行政區"]):

                        result.append(
                            f"🏠 {row['標題']}\n"
                            f"📍 {row['行政區']}\n"
                            f"💰 {row['租金']}\n"
                            f"🔗 {row['網址']}"
                        )

                if result:
                    message_text = "\n\n".join(result[:5])
                else:
                    message_text = f"找不到 {area} 的案件"

            elif text == "今日案件":
                message_text = "今日案件功能建置中"

            elif text == "租補客":
                message_text = "租補客功能建置中"

            elif text == "FB租客":
                message_text = "FB租客功能建置中"

            with ApiClient(configuration) as api_client:

                line_bot_api = MessagingApi(api_client)

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[
                            TextMessage(text=message_text)
                        ]
                    )
                )

    except Exception as e:
        print("ERROR:", e)

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
