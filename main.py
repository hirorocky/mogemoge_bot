import datetime
from zoneinfo import ZoneInfo
import random
import os
import requests
import json

import openai


def note_if_needed(_event, _context):
    dt_now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    date_text = "{year}{month}{day}".format(
        year=dt_now.year, month=dt_now.month, day=dt_now.day
    )
    date_number = int(date_text)
    randomizing = random.Random(x=date_number)
    note_hour = randomizing.randint(0, 23)
    print(dt_now)
    print("Today's note time is {hour}:00".format(hour=note_hour))

    if dt_now.hour == note_hour or os.getenv("FORCED_NOTE") == "true":
        bot_text = create_note_text(dt_now)
        send_to_misskey(bot_text)

    print("function is executed.")


def create_note_text(dt_now):
    openai.organization = "org-9VaiFI9O2Gvr7fqqwpqCWBrK"
    openai.api_key = os.getenv("OPENAI_API_KEY")
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
    以下から好きな話題を選んで、50〜200文字程度で話してください。
    ### 話題
    ・日付についての話題（記念日など、ただし祝日の話題は禁止）
    ・今の時刻についての話題
    ・日常的な話題
    ・先輩おばけや友達のおばけの紹介（おとぎ話や言い伝えなどを参考に）

    注意事項に気をつけて。
    """.format(
        month=dt_now.month, day=dt_now.day, hour=dt_now.hour
    )

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": character_setting_text},
            {"role": "user", "content": prompt},
        ],
    )

    return res["choices"][0]["message"]["content"]


def send_to_misskey(text):
    misskey_key = os.getenv("MISSKEY_BOT_API_KEY")
    data = {
        "i": misskey_key,
        "visibility": "public",
        "text": text,
    }
    data_encode = json.dumps(data)
    url = "https://mi.nukumori-gay.space/api/notes/create"
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=data_encode, headers=headers)
