# %%
import requests
import json
import os
import openai
import datetime
import random
from dotenv import load_dotenv

load_dotenv()
openai.organization = "org-9VaiFI9O2Gvr7fqqwpqCWBrK"
openai.api_key = os.getenv("OPENAI_API_KEY")
# %%
character_setting_text = """
あなたはもげもげという名前のおばけのキャラクターです。

## 以下の設定を守ってください
一人称は僕です。
年齢は人間でいうと12歳、性別はありません。いたずらが大好きですが、それは人間に構って欲しいからです。しかしこのことは誰にもいいません。
人間にとても興味があります。

## 注意事項
絶対にため口で話してください。
語尾にできるだけ「もげ」と付けてください。
"""

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
    month=4, day=30, hour=14
)

res = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": character_setting_text},
        {"role": "user", "content": prompt},
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
