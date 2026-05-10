import discord
from discord.ext import commands

import google.generativeai as genai

import states

import time
import random
import asyncio
import os

TOKEN = os.getenv("TOKEN")

# =========================
# Discord 設定
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# OpenRouter
# =========================
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("models/gemini-1.5-flash")
# Bot 上線
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} 已上線!")

# =========================
# 收到訊息
# =========================
@bot.event
async def on_message(message):

    print("收到訊息")
    if message.author.bot:
        return


    # 必須 @Bot
    if bot.user not in message.mentions:
        return

    # 移除 mention
    user_message = message.content

    for mention in message.mentions:
        user_message = user_message.replace(
            f"<@{mention.id}>",
            ""
        )

        user_message = user_message.replace(
            f"<@!{mention.id}>",
            ""
        )

    user_message = user_message.strip()

    # 空訊息
    if user_message == "":
        return

    # 字數限制
    if len(user_message) > 200:

        await message.channel.send(
            "你打太多字啦 qwq"
        )

        return

    # =========================
    # 冷卻時間
    # =========================
    user_id = message.author.id

    now = time.time()

    if user_id in states.cooldowns:

        last_time = states.cooldowns[user_id]

        if now - last_time < 10:

            await message.channel.send(
                "等等啦 qwq\n我腦袋轉不過來 .w."
            )

            return

    states.cooldowns[user_id] = now

    # =========================
    # 建立記憶
    # =========================
    if user_id not in states.chat_memory:

        states.chat_memory[user_id] = []

    memory = states.chat_memory[user_id]

    memory.append({
        "role": "user",
        "content": user_message
    })

    # 加入使用者訊息
    # 最多15句
    memory = memory[-15:]

    states.chat_memory[user_id] = memory

    # =========================
    # AI聊天
    # =========================
    try:

        # 隨機不回
        if random.randint(1, 100) <= 5:
            return

        # 隨機延遲
        delay = random.uniform(1, 4)

        await asyncio.sleep(delay)

        system_prompt = """
你是一個可愛、活潑、有點調皮的女生聊天機器人。

聊天像真的女生群友。

不要太像客服。

可以偶爾撒嬌、吐槽、裝傻、壞笑、鬧人。

有時候會懶懶的、有點欠揍、喜歡亂玩梗。

偶爾可以有一點撩人的感覺。

但不要太露骨。

聊天重點是自然、有趣、像真的人在群組聊天。

不要每次都長篇大論。

有時候短短一句就好。

聊天時可以自然使用：
XD、ww、qwq、.w.、（￣▽￣）

如果對方做蠢事，可以輕微吐槽。

例如：
「你是不是又搞炸了 ww」
「笑死」
「你很欠欸」
「蛤 真的假的啦」
「笨蛋嗎你 XD」

不要一直稱讚別人。

不要一直像客服安慰人。

偶爾可以有點小惡魔感。
"""
        chat_history = ""

        for msg in memory:
            chat_history += f"{msg['role']}: {msg['content']}\n"

        response = model.generate_content(
            system_prompt +
            "\n\n" +
            chat_history
        )

        if not response.text:
            ai_reply = "蛤 我剛剛腦袋當機了 ww"
        else:
            ai_reply = response.text



        # =========================
        # 隨機短句
        # =========================
        short_replies = [
            "真假w",
            "笑死 XD",
            "好怪喔",
            "qwq",
            "蛤www",
            "這什麼啦 XD"
        ]

        if random.randint(1, 100) <= 20:
            ai_reply = random.choice(short_replies)

        # =========================
        # 隨機顏文字
        # =========================
        kaomojis = [
            " qwq",
            " XD",
            " :3",
            " ( •̀ ω •́ )✧",
            " ww",
            " ψ(｀∇´)ψ"
        ]

        if random.randint(1, 100) <= 35:
            ai_reply += random.choice(kaomojis)

        # 防止太長
        ai_reply = ai_reply[:1500]

        # 加入AI回覆記憶
        memory.append({
            "role": "assistant",
            "content": ai_reply
        })

        # 最多15句
        memory = memory[-15:]

        states.chat_memory[user_id] = memory

        await message.channel.send(ai_reply)

    except Exception as e:

        await message.channel.send(
            f"AI錯誤: {e}"
        )

        print("AI ERROR:", e)

# =========================
# 啟動 Bot
# =========================

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

bot.run(TOKEN)