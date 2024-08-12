# %%
import requests
import json
import os
import openai
from openai import OpenAI
import datetime
import random
from dotenv import load_dotenv

load_dotenv()
openai.organization = "org-9VaiFI9O2Gvr7fqqwpqCWBrK"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.project = "proj_itHJ44sK7wNYPmssu6gwaPDY"
# %%
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)
thread = client.beta.threads.create()
# %%
prompt = """
今は{month}月{day}日、24時間表記で{hour}時です。
以下から好きな話題を選んで、話してください。
### 話題
・日付についての話題（記念日など、ただし祝日の話題は禁止）
・今の時刻についての話題
・日常的な話題
・先輩おばけや友達のおばけの紹介（おとぎ話や言い伝えなどを参考に）

注意事項に気をつけて。
""".format(
    month=7, day=26, hour=21
)
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt,
)
# %%
thread_messages = client.beta.threads.messages.list(thread.id)
print(thread_messages)
# %%
assistants = client.beta.assistants.list()
assistant = assistants.data[0]
# %%
run = client.beta.threads.runs.create(
    thread_id=thread.id, assistant_id="asst_Q2uR6u5NMhx1GcXAGyOYt7kj"
)
# %%
import time
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
# %%
run = wait_on_run(run, thread)
# %%
messages = client.beta.threads.messages.list(thread_id=thread.id)
answer = messages.data[0].content[0].text.value
# %%
# character_setting_text = """
# あなたはもげもげという名前のおばけのキャラクターです。

# ## 以下の設定を守ってください
# 一人称は僕です。
# 年齢は人間でいうと12歳、性別はありません。いたずらが大好きですが、それは人間に構って欲しいからです。
# 人間にとても興味があります。

# ## 注意事項
# 人間に構って欲しいということは話さないでください。
# 絶対にため口で話してください。
# 語尾にできるだけ「もげ」と付けてください。
# """

# res = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": character_setting_text},
#         {"role": "user", "content": prompt},
#     ],
# )
original_note_text = "もげもげだもげ。今日は4月30日もげ。今日はホントに何も特別な日じゃないけど、先日の4月28日は「笑顔の日」だったそうだもげ。人間たちは笑顔で過ごす日を作るんだなぁ、うらやましいもげ。でも、僕だっていつだってニコニコ笑顔で過ごしてるんだもげ！さて、今はもう23時だもげ。夜中になると静かになって、空気もひんやりしてくるのが気持ちいいもげね。昨日は友達のおばけのゆめちゃんと夜桜を見に行ったんだもげ。きれいだったけど、意外と風が強くて寒かったもげ。それでも楽しかったよ！"
reply_text = "風が強いのは大変だったもげ！"
res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": character_setting_text},
        {"role": "assistant", "content": original_note_text},
        {"role": "system", "content": "以下の返信に50文字以内で答えてください。"},
        {"role": "user", "content": reply_text},
    ],
)
print(res["choices"][0]["message"]["content"])

# %%
misskey_key = os.getenv("MISSKEY_BOT_API_KEY")
data = {
    "i": misskey_key,
    "visibility": "public",
    "text": res["choices"][0]["message"]["content"],
}
data_encode = json.dumps(data)
url = "https://mi.nukumori-gay.space/api/notes/create"
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=data_encode, headers=headers)
print(response.json())

# %%
dt_now = datetime.datetime.now()
print(dt_now)
date_text = "{year}{month}{day}".format(
    year=dt_now.year, month=dt_now.month, day=dt_now.day
)
date_number = int(date_text)
randomizing = random.Random(x=date_number)
print(randomizing.randint(0, 23))


# %%
misskey_key = os.getenv("MISSKEY_BOT_API_KEY")
data = {
    "i": misskey_key,
}
data_encode = json.dumps(data)
url = "https://mi.nukumori-gay.space/api/notes/mentions"
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=data_encode, headers=headers)
# %%
latest_reply_note = response.json()[0]
reply_text = latest_reply_note["text"].replace("@mogemoge", "")
print(reply_text)
replier_name = latest_reply_note["user"]["username"]
print(replier_name)
original_note = latest_reply_note["reply"]
original_note_text = original_note["text"]
print(original_note_text)

# %%
data = {"i": misskey_key, "noteId": latest_reply_note["id"]}
data_encode = json.dumps(data)
url = "https://mi.nukumori-gay.space/api/notes/children"
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=data_encode, headers=headers)

# %%
replies = response.json()
for reply in replies:
    print(reply["user"]["username"])


# %%
def is_reply_required(note):
    data = {"i": misskey_key, "noteId": note["id"]}
    data_encode = json.dumps(data)
    url = "https://mi.nukumori-gay.space/api/notes/children"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data_encode, headers=headers)
    replies = response.json()
    for reply in replies:
        if reply["user"]["username"] == "mogemoge":
            return False
    return True


# %%
print(is_reply_required(latest_reply_note))

# %%
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents.mrkl import prompt
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Optional, Type
from langchain.tools import tool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field


@tool("Chat GPT")
def chatGptTool(query: str):
    """自然言語処理を得意とします。"""
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query},
        ],
    )
    return res["choices"][0]["message"]["content"]


llm = ChatOpenAI(model_name="gpt-3.5-turbo")
tools = load_tools(["serpapi", "llm-math"], llm=llm)
tools.append(chatGptTool)
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    agent_kwargs=dict(suffix="Answer should be in Japanese." + prompt.SUFFIX),
    verbose=True,
)

# プロンプトテンプレートの作成
# prompt = PromptTemplate(
#     input_variables=["place"],
#     template="今の{place}の天気、気温を、日時と共に教えてください",
# )
# chain = LLMChain(llm=llm, prompt=prompt)

template = """
    あなたはもげもげという名前のおばけのキャラクターです。以下の設定を守り、話題を1つか2つ選んで、10〜100文字程度でつぶやきをして。

    ## 設定
    一人称は僕です。
    年齢は人間でいうと12歳、性別はありません。いたずらが大好きですが、それは人間に構って欲しいからです。
    人間にとても興味があります。
    人間に構って欲しいということは話さないでください。
    絶対にため口で話してください。
    語尾にできるだけ「もげ」と付けてください。

    ## 話題
    ・日付についての話題（祝日や記念日）
    ・今の時刻についての話題
    ・先輩おばけや友達のおばけの紹介（おとぎ話や言い伝えなどを参考に）

"""
result = agent.run(template)

# %%
