from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
import asyncio
import re
import time

api_id = 29381099
api_hash = 'd03a2742fc1a23d7d520fc4412dd9851'
client = TelegramClient('jasurn6', api_id, api_hash)

clients = [
    client,
    TelegramClient('maxmudovku', 27996139, '8057566b4d48b75b351a2979d20171b0'),
    TelegramClient('halol_bolamen', 27890211, 'b6edf9b6b68185c9b018e4263c9980bc'),
    TelegramClient('maxmudovk', 21266546, 'add6e254faf19039cc2db89b495999bb'),
    TelegramClient('soqqa_topuvchi', 25924006, '8f237939099b8f2f817fb1471595525b'),
    TelegramClient('soqqa_tekin', 26700474, '9d636255d4d5a1ec6958028614bbc1c5'),
    TelegramClient('pubger_bola_men', 23719464, 'c2bb6053b548dc85b46775176caefb26'),
    TelegramClient('uzbeklarni1', 29213728, 'edca4ad93432a95a9af8ffe4f945d62d'),
    TelegramClient('jasur_1234567890', 29345186, '0cfe0ec8213182b255f2ffb6954ac8d2'),
    TelegramClient('killer_bola_man', 20466561, '7d297986052b1e4bd8231c239247956d'),
]

# 💤 Delay oralig‘i sekundlarda: 0 = to‘xtashsiz
delay_between_actions = 0.31000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001

selected_script = step = forwarded_channel = trigger_text = post_id = None
reply_texts = []

@client.on(events.NewMessage(chats='me', pattern=r'^/help$'))
async def help_handler(event):
    global selected_script, step, forwarded_channel, trigger_text, reply_texts, post_id
    selected_script = step = forwarded_channel = trigger_text = post_id = None
    reply_texts.clear()
    await event.respond(
        "1. Post kommentiga reply yozish\n"
        "2. Kanal postiga trigger chiqqanda avtomatik reply\n"
        "3. Kanal chatiga xabar yuborish\n"
        "4. Kanal yoki chatga barcha akkauntlarni a’zo qilish\n\n"
        "Raqamni yuboring:")

@client.on(events.NewMessage(chats='me', pattern=r'^[1-4]$'))
async def select_variant(event):
    global selected_script, step
    selected_script = event.raw_text.strip()
    step = {"1": "post_link", "2": "channel_input", "3": "group_input", "4": "join_target"}[selected_script]
    messages = {
        "post_link": "📨 Post linkini forward qiling yoki link tashlang:",
        "channel_input": "📨 Kanal postini forward qiling yoki link yuboring:",
        "group_input": "📨 Kanalni yuboring (chatga bog‘langan bo‘lishi kerak):",
        "join_target": "📥 Kanal yoki guruh linkini yuboring (barcha akkauntlar qo‘shiladi):"
    }
    await event.respond(messages[step])

@client.on(events.NewMessage(chats='me'))
async def step_handler(event):
    global step, forwarded_channel, trigger_text, reply_texts, post_id
    text = event.raw_text.strip()
    fwd = event.message.forward

    if selected_script == "1" and step == "post_link":
        if fwd and fwd.chat:
            forwarded_channel = fwd.chat
            post_id = fwd.channel_post
        else:
            match = re.match(r'https://t\.me/([\w_]+)/([0-9]+)', text)
            if match:
                forwarded_channel = await client.get_entity(match.group(1))
                post_id = int(match.group(2))
            else:
                return await event.respond("❌ Link xato.")
        step = "replies"
        return await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")

    elif selected_script in ("2", "3") and step in ("channel_input", "group_input"):
        entity = fwd.chat if fwd and fwd.chat else None
        if not entity:
            match = re.match(r'https://t\.me/([\w_]+)', text)
            if match:
                entity = await client.get_entity(match.group(1))
        if not entity:
            return await event.respond("❌ Kanalni topib bo‘lmadi.")
        if selected_script == "2":
            forwarded_channel = entity
            step = "trigger"
            return await event.respond("🔑 Trigger so‘zini kiriting:")
        else:
            full = await client(GetFullChannelRequest(entity))
            if full.full_chat.linked_chat_id:
                forwarded_channel = full.full_chat.linked_chat_id
                step = "chat_replies"
                return await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")
            else:
                return await event.respond("❌ Kanalga chat ulangan emas.")

    elif selected_script == "2" and step == "trigger":
        trigger_text = text
        step = "replies"
        return await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")

    elif selected_script == "4" and step == "join_target":
        match = re.match(r'https://t\.me/([\w_]+)', text)
        if not match:
            return await event.respond("❌ Link xato.")
        username = match.group(1)
        await event.respond("🔄 Kanal/guruhga qo‘shilmoqda...")
        await run_variant4_join(username)
        return await event.respond("✅ Barcha akkauntlar qo‘shildi.")

    elif step in ("replies", "chat_replies"):
        reply_texts = [line.strip() for line in text.splitlines() if line.strip()]
        if len(reply_texts) != 10:
            return await event.respond("❌ Iltimos, aynan 10 ta reply yuboring.")
        await event.respond("✅ Ishga tushyapti...")
        func = {"1": run_variant1, "2": run_variant2_monitor, "3": run_variant3_chat}.get(selected_script)
        if func:
            await func()

async def run_variant1():
    await asyncio.gather(*[c.start() for c in clients])
    async def send_reply(i):
        try:
            await asyncio.sleep(delay_between_actions)
            channel = await clients[i].get_entity(forwarded_channel)
            result = await clients[i](GetDiscussionMessageRequest(peer=channel, msg_id=post_id))
            discussion_msg = next((m for m in result.messages if m.id != post_id), None)
            if discussion_msg:
                await clients[i].send_message(entity=discussion_msg.to_id, message=reply_texts[i], reply_to=discussion_msg.id)
                print(f"[{i+1}] ✅ Reply yuborildi.")
        except Exception as e:
            print(f"[{i+1}] ⚠️ Xatolik: {e}")
    await asyncio.gather(*[send_reply(i) for i in range(10)])

async def run_variant2_monitor():
    await asyncio.gather(*[c.start() for c in clients])
    @clients[0].on(events.NewMessage(chats=getattr(forwarded_channel, 'username', forwarded_channel.id)))
    async def listen(event):
        msg = event.message
        if msg.text and trigger_text.lower() in msg.text.lower():
            print("✅ Trigger topildi:", msg.text)
            await asyncio.gather(*[send_reply_with_retry(clients[i], msg.id, reply_texts[i], i+1) for i in range(10)])
    print("📱 Trigger monitoring boshlandi")
    await clients[0].run_until_disconnected()

async def send_reply_with_retry(client, msg_id, reply_text, number):
    try:
        await asyncio.sleep(delay_between_actions)
        channel = await client.get_entity(forwarded_channel)
        result = await client(GetDiscussionMessageRequest(peer=channel, msg_id=msg_id))
        discussion_msg = next((m for m in result.messages if m.id != msg_id), None)
        if discussion_msg:
            await client.send_message(entity=discussion_msg.to_id, message=reply_text, reply_to=discussion_msg.id)
            print(f"[{number}] ✅ Reply yuborildi.")
    except Exception as e:
        print(f"[{number}] ❌ Urinish: {e}")

async def run_variant3_chat():
    await asyncio.gather(*[c.start() for c in clients])
    async def send_chat(i):
        try:
            await asyncio.sleep(delay_between_actions)
            await clients[i].send_message(forwarded_channel, reply_texts[i])
            print(f"[{i+1}] ✅ Chatga yuborildi.")
        except Exception as e:
            print(f"[{i+1}] ❌ Xatolik: {e}")
    await asyncio.gather(*[send_chat(i) for i in range(10)])

async def run_variant4_join(username):
    await asyncio.gather(*[c.start() for c in clients])
    async def join(i):
        try:
            await asyncio.sleep(delay_between_actions)
            entity = await clients[i].get_entity(username)
            await clients[i](JoinChannelRequest(channel=entity))
            print(f"[{i+1}] ✅ Kanalga qo‘shildi: {username}")
            full = await clients[i](GetFullChannelRequest(entity))
            if full.full_chat.linked_chat_id:
                group = await clients[i].get_entity(full.full_chat.linked_chat_id)
                await clients[i](JoinChannelRequest(channel=group))
                print(f"[{i+1}] ✅ Chatga ham qo‘shildi.")
        except Exception as e:
            print(f"[{i+1}] ⚠️ Xatolik: {e}")
    await asyncio.gather(*[join(i) for i in range(10)])

async def main():
    start_time = time.time()
    await client.start()
    print(f"🤖 Jasur bot tayyor ({time.time() - start_time:.2f} s)")
    await client.run_until_disconnected()

asyncio.run(main())

# Bu qism faylingizning eng oxiriga joylashtiriladi
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()

