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
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(CHANNEL_SECRET)


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

    try:
        handler.handle(body, signature)
        print("HANDLE SUCCESS")

    except Exception as e:
        print("HANDLE ERROR")
        print(e)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    print("================================")
    print("收到訊息")
    print(event.message.text)
    print("================================")

    try:

        with ApiClient(configuration) as api_client:

            line_bot_api = MessagingApi(api_client)

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text="測試成功"
                        )
                    ]
                )
            )

        print("回覆成功")

    except Exception as e:

        print("回覆失敗")
        print(e)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
