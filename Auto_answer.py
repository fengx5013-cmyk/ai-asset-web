import time
from collections import defaultdict

# ===== 1) WeChat 自动化：兼容 weixin-auto(wxauto) / wxautox =====
WeChat = None
_import_err = None

try:
    # weixin-auto 通常提供 wxauto 模块
    from wxauto import WeChat  # type: ignore
except Exception as e1:
    _import_err = e1
    try:
        # 如果你装的是 wxautox
        from wxautox import WeChat  # type: ignore
        _import_err = None
    except Exception as e2:
        _import_err = (e1, e2)

if WeChat is None:
    raise RuntimeError(f"无法导入 WeChat。请确认安装的是 weixin-auto 或 wxautox。错误: {_import_err}")

# ===== 2) 智谱/ZAi SDK =====
from zai._client import ZaiClient# 来自 z-ai-sdk-python :contentReference[oaicite:3]{index=3}

# ===== 3) 初始化 =====
wx = WeChat()
client = ZaiClient(api_key="7c27ea802dac43628d23e1ffd4a1a2de.lOQ408znUubE4n8v")  # ←替换成真实Key

SYSTEM_PROMPT = "你是我的积极向上的女朋友，我们进行日常对话聊天。"

# 每个好友一份对话历史
history_map = defaultdict(lambda: [{"role": "system", "content": SYSTEM_PROMPT}])

# 用于“去重”：记录每个好友最近处理过的消息特征
last_seen_map = {}  # friend_key -> (content, timestamp_str)


def get_ai_response(history):
    """获取AI回复（非流式）"""
    resp = client.chat.completions.create(
        model="glm-4.5-flash",   # 角色扮演/拟人模型 :contentReference[oaicite:4]{index=4}
        messages=history,
        stream=False
    )
    return resp.choices[0].message.content


def normalize_friend_key(msg):
    """
    尽量用备注名作为好友key；没有就退化到发送者字段。
    不同包/版本字段名可能略有差异，所以这里做容错。
    """
    for k in ("sender_remark", "sender", "fromUser", "talker"):
        if hasattr(msg, k) and getattr(msg, k):
            return str(getattr(msg, k))
    return "UNKNOWN_FRIEND"


def normalize_content(msg):
    for k in ("content", "text", "msg", "message"):
        if hasattr(msg, k) and getattr(msg, k) is not None:
            return str(getattr(msg, k))
    return ""


def normalize_time(msg):
    # wxauto/wxautox 有的消息对象带 time 字段，有的没有；没有就用当前时间粗略去重
    for k in ("time", "timestamp", "create_time"):
        if hasattr(msg, k) and getattr(msg, k):
            return str(getattr(msg, k))
    return str(int(time.time()))


def is_friend_message(msg):
    """
    不同实现里 type 的取值可能不一样，这里做“宽松判断”：
    - 如果 msg.type 存在且包含 friend/chat/text 等关键词就认为是对方消息
    - 同时尽量排除 self/me 之类自己发的消息
    """
    t = ""
    if hasattr(msg, "type") and getattr(msg, "type") is not None:
        t = str(getattr(msg, "type")).lower()

    # 常见：friend / text / recv 等；排除 self / me / send 等
    if any(x in t for x in ("self", "me", "send", "mine")):
        return False

    if t == "":
        # 没有 type 字段时：只能依赖“能拿到 sender 且不是空”来推断
        return True

    return any(x in t for x in ("friend", "recv", "receive", "text", "chat", "msg"))


def append_and_trim(history, role, content, max_len=20):
    history.append({"role": role, "content": content})
    # 保留 system + 最近 max_len-1 条
    if len(history) > max_len:
        history[:] = [history[0]] + history[-(max_len - 1):]


# ===== 4) 主循环：监听并回复 =====
while True:
    try:
        msgs = wx.GetAllMessage()
        if msgs:
            latest = msgs[-1]

            if is_friend_message(latest):
                friend_key = normalize_friend_key(latest)
                user_input = normalize_content(latest).strip()
                msg_time = normalize_time(latest)

                # 空消息不处理
                if not user_input:
                    time.sleep(1)
                    continue

                # 去重：同一好友同一条内容+时间（或近似时间）只处理一次
                last_seen = last_seen_map.get(friend_key)
                cur_seen = (user_input, msg_time)
                if last_seen == cur_seen:
                    time.sleep(1)
                    continue

                last_seen_map[friend_key] = cur_seen

                print(f"[收到] {friend_key}: {user_input}")

                history = history_map[friend_key]
                append_and_trim(history, "user", user_input)

                ai_reply = get_ai_response(history).strip()
                print(f"[回复] {friend_key}: {ai_reply}")

                append_and_trim(history, "assistant", ai_reply)

                # 发送：先切到该好友窗口，再发消息
                wx.ChatWith(friend_key)
                wx.SendMsg(ai_reply)

    except Exception as e:
        print(f"发生错误: {e}")

    time.sleep(5)  # 建议 2s 左右，5s也行；太快可能影响微信窗口稳定性




# import zai
# print(zai.__version__)