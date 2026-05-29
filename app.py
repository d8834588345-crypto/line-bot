@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):

    user_text = event.message.text.strip()

    try:

        data = sheet.get_all_records()

        print("==========")
        print("工作表名稱：", sheet.title)
        print("資料筆數：", len(data))
        print(data[:3])
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

        print("查詢錯誤：", str(e))
        reply_text = f"查詢失敗：{str(e)}"

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
