# 运行前务必执行“!pip install --upgrade openai”，确保openai模块版本号为1.2.3或更高
from openai import OpenAI
from dotenv import load_dotenv
import time
import os
from flask import Flask, render_template, request 
load_dotenv()
client = OpenAI()
assistant = client.beta.assistants.retrieve("asst_Toevazny9ckiIZiR2AtBhplR") # assistantID

app = Flask(__name__)

thread = client.beta.threads.create() # 创建线程

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def completion_response():
    user_input = request.args.get('msg') # 获取用户输入的内容
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run
    run = wait_on_run(run, thread)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    # 创建信息对象
    message = client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_input
    )
    # 创建运行对象
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    # 等待运行完成
    wait_on_run(run, thread)
    # 检索回复内容
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, order="asc", after=message.id # 升序排列
    )
    for msg in messages.data:
        if msg.role == "assistant":
            response = msg.content[0].text.value # 获取助手的响应内容
    return str(response) # 返回助手的响应内容
# 启动Flask应用
if __name__ == "__main__":
    app.run()
    
