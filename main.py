import datetime
from zoneinfo import ZoneInfo
import random
import os
import requests
import json
from openai import OpenAI
import time

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)
misskey_key = os.getenv("MISSKEY_BOT_API_KEY")


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
        bot_text = create_daily_note_text(dt_now)
        send_to_misskey(bot_text)
        print("daily note is created.")

    latest_reply = get_latest_reply_note()
    if is_reply_required(latest_reply):
        reply_text = create_reply_note_text(latest_reply)
        send_to_misskey(reply_text, replyId=latest_reply["id"])
        print("reply to {text}".format(text=latest_reply["text"]))

    print("function is executed.")


def create_daily_note_text(dt_now):
    prompt = """
    今は{month}月{day}日、24時間表記で{hour}時です。
    以下から好きな話題を1つか2つ選んで、10〜100文字程度で話してください。
    ### 話題
    ・日付についての話題（祝日の話題は禁止）
    ・今の時刻についての話題
    ・日常的な話題（あいさつなど）
    ・先輩おばけや友達のおばけの紹介（おとぎ話や言い伝えなどを参考に）

    注意事項に気をつけて。
    """.format(
        month=dt_now.month, day=dt_now.day, hour=dt_now.hour
    )

    thread = openai_client.beta.threads.create()
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    return get_assistant_response(thread)


def create_reply_note_text(reply_note):
    thread = openai_client.beta.threads.create()

    reply_text = reply_note["text"].replace("@mogemoge", "")
    replier_name = reply_note["user"]["username"]

    if "reply" in reply_note:
        original_note = reply_note["reply"]
        original_note_text = original_note["text"]
        openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="assistant",
            content=original_note_text,
        )

    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="以下の返信に50文字以内で答えてください",
    )
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=reply_text,
    )

    return "@{mention} {text}".format(
        mention=replier_name, text=get_assistant_response(thread)
    )


def get_latest_reply_note():
    data = {
        "i": misskey_key,
    }
    data_encode = json.dumps(data)
    url = "https://mi.nukumori-gay.space/api/notes/mentions"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data_encode, headers=headers)
    replies = response.json()
    return replies[0]


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


def get_assistant_response(thread):
    assistants = openai_client.beta.assistants.list()
    assistant = assistants.data[0]
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )
    while run.status == "queued" or run.status == "in_progress":
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value


def send_to_misskey(text, replyId=None):
    data = {
        "i": misskey_key,
        "visibility": "public",
        "text": text,
        "replyId": replyId,
    }
    data_encode = json.dumps(data)
    url = "https://mi.nukumori-gay.space/api/notes/create"
    headers = {"Content-Type": "application/json"}
    requests.post(url, data=data_encode, headers=headers)


if __name__ == "__main__":
    note_if_needed(None, None)
