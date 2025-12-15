from flask import Flask, request, jsonify, send_from_directory
from zai import ZhipuAiClient
import os


print("DEBUG ZHIPU_API_KEY =", os.getenv("ZHIPU_API_KEY"))

app = Flask(__name__, static_folder="static")
client = ZhipuAiClient(api_key=os.getenv("ZHIPU_API_KEY"))

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = (data.get("message") or "").strip()
    if not user_msg:
        return jsonify({"reply": "你好呀。"}), 400

    try:
        response = client.chat.completions.create(
            model="charglm-4",
            messages=[
                {"role": "system", "content": "你是我的积极向上的女朋友，有一些小脾气，我们进行日常对话聊天。"},
                {"role": "user", "content": user_msg}
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"对话结束，期待下次再聊！"}), 500

if __name__ == "__main__":
    # 本地运行用；线上 Render 用 gunicorn 启动，不走这里
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
