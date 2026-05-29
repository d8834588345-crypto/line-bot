from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "LINE Bot Running"

@app.route("/callback", methods=["POST"])
def callback():

    print("WEBHOOK HIT")
    print(request.get_json())

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
