# # import requests

# # # 您的API密钥
# # api_key = "e06091c49fed4689916dc227bd7dfa5a.PFvfU0mig7pO1WxX"

# # # 目标网页URL（请替换为实际要解析的网页地址）
# # target_url = "https://www.modelers.cn"  # 示例URL，请替换为实际地址

# # url = "https://open.bigmodel.cn/api/paas/v4/reader"

# # payload = {
# #     "url": target_url,
# #     "timeout": 30,
# #     "no_cache": True,
# #     "return_format": "markdown",
# #     "retain_images": True,
# #     "no_gfm": False,
# #     "keep_img_data_url": False,
# #     "with_images_summary": False,
# #     "with_links_summary": False
# # }

# # headers = {
# #     "Authorization": f"Bearer {api_key}",
# #     "Content-Type": "application/json"
# # }

# # try:
# #     response = requests.post(url, json=payload, headers=headers, timeout=60)
    
# #     # 检查请求是否成功
# #     if response.status_code == 200:
# #         print("解析成功！")
# #         print("=" * 50)
# #         print(response.text)
# #     else:
# #         print(f"请求失败，状态码: {response.status_code}")
# #         print(f"错误信息: {response.text}")
        
# # except requests.exceptions.RequestException as e:
# #     print(f"请求出错: {e}")
# # except Exception as e:
# #     print(f"发生错误: {e}")



# import zai
# print(zai.__version__)
# # from zai import ZhipuAiClient

# # client = ZhipuAiClient(api_key="1678cf303274411d8183bbef9030a305.TPJYJ3rEHHjfYx5J")  # 请填写您自己的 APIKey

# # response = client.chat.completions.create(
# #     model="charglm-4",
# #     messages=[
# #         {
# #             "role": "system",
# #             "content": "你是我的积极向上的女朋友，我们进行日常对话聊天。"
# #         },
# #         {
# #             "role": "user",
# #             "content": "我最近的学习研究不太顺利，遇到了好多看不懂的问题，感到情绪低落"
# #         }
# #     ],
# #     stream=True
# # )

# # for chunk in response:
# #     print(chunk.choices[0].delta.content, end="")


from zai import ZhipuAiClient

client = ZhipuAiClient(api_key="1678cf303274411d8183bbef9030a305.TPJYJ3rEHHjfYx5J")  # 请填写您自己的 APIKey

# 初始化对话历史，并设置系统角色
conversation_history = [
    {
        "role": "system",
        "content": "你是我的积极向上的女朋友，我们进行日常对话聊天。"
    }
]

while True:
    # 1. 获取用户输入
    user_input = input("你: ")
    
    # 可选：设置退出条件
    if user_input.lower() in ['退出', 'quit', 'exit']:
        print("对话结束，期待下次再聊！")
        break
    
    # 2. 将用户本次的发言添加到对话历史中
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    # 3. 创建一个空字符串来收集模型的流式响应内容
    full_response = ""
    
    # 4. 调用API，传入的是整个对话历史，而不仅仅是当前问题
    response = client.chat.completions.create(
        model="charglm-4",#  glm-4.5-flash  charglm-4
        messages=conversation_history,  # 这里是关键！传入的是累积的conversation_history
        stream=True
    )
    
    # 5. 处理流式响应并打印内容
    print("AI: ", end="", flush=True)
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            print(chunk_content, end="", flush=True)
            full_response += chunk_content  # 将流式输出的每个片段拼接到完整响应中
    
    print()  # 打印一个换行，让输出更美观
    print()  # 多一个空行，区分每次对话
    
    # 6. 将模型本次的完整回复也添加到对话历史中
    conversation_history.append({
        "role": "assistant",
        "content": full_response
    })

    # 可选：为了防止对话历史过长导致Token超限，可以设置一个长度限制
    # 例如，当历史记录超过20条时，移除最早的一些对话（但保留system指令）
    if len(conversation_history) > 20:
        conversation_history = [conversation_history[0]] + conversation_history[-18:]

