from flask import Flask, request
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "/etc/secrets/google-credentials.json",
    scopes=SCOPES
)

gc = gspread.authorize(creds)

@app.route("/")
def home():
    return "LINE Bot Running"

@app.route("/callback", methods=["POST"])
def callback():

    body = request.get_json()

    print(body)

    try:

        events = body.get("events", [])

        for event in events:

            if event.get("type") != "message":
                continue

            text = event["message"]["text"]

            if text.startswith("找 "):

                area = text.replace("找 ", "").strip()

                sheet = gc.open_by_key(SHEET_ID).worksheet("出租案件")

                rows = sheet.get_all_records()

                result = []

                for row in rows:

                    if area in str(row["行政區"]):

                        result.append(
                            f"""
🏠 {row['標題']}
📍 {row['行政區']}
💰 {row['租金']}
🔗 {row['網址']}
"""
                        )

                print(result)

    except Exception as e:
        print(e)

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
