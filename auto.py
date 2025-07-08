from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
import asyncio
import re

# === Asosiy akkaunt ===
api_id = 29381099
api_hash = 'd03a2742fc1a23d7d520fc4412dd9851'
client = TelegramClient('jasurn6', api_id, api_hash)

# === 10 ta akkaunt ===
clients = [
    client,  # 1
    TelegramClient('maxmudovku', 27996139, '8057566b4d48b75b351a2979d20171b0'),  # 2
    TelegramClient('halol_bolamen', 27890211, 'b6edf9b6b68185c9b018e4263c9980bc'),  # 3
    TelegramClient('maxmudovk', 21266546, 'add6e254faf19039cc2db89b495999bb'),  # 4
    TelegramClient('soqqa_topuvchi', 25924006, '8f237939099b8f2f817fb1471595525b'),  # 5
    TelegramClient('soqqa_tekin', 26700474, '9d636255d4d5a1ec6958028614bbc1c5'),  # 6
    TelegramClient('pubger_bola_men', 23719464, 'c2bb6053b548dc85b46775176caefb26'),  # 7
    TelegramClient('uzbeklarni1', 29213728, 'edca4ad93432a95a9af8ffe4f945d62d'),  # 8
    TelegramClient('jasur_1234567890', 29345186, '0cfe0ec8213182b255f2ffb6954ac8d2'),  # 9
    TelegramClient('killer_bola_man', 20466561, '7d297986052b1e4bd8231c239247956d'),  # 10
]

# === Global o‘zgaruvchilar ===
selected_script = None
step = None
forwarded_channel = None
trigger_text = None
reply_texts = []
post_id = None

@client.on(events.NewMessage(chats='me', pattern=r'^/help$'))
async def help_handler(event):
    global selected_script, step, forwarded_channel, trigger_text, reply_texts, post_id
    selected_script = None
    step = None
    forwarded_channel = None
    trigger_text = None
    reply_texts = []
    post_id = None
    await event.respond(
        "Qaysi kodni ishga tushiray?\n\n"
        "1. Post kommentiga reply yozish\n"
        "2. Kanal postiga trigger chiqqanda avtomatik reply\n"
        "3. Kanal chatiga xabar yuborish\n"
        "4. Kanal yoki chatga barcha akkauntlarni a’zo qilish\n\n"
        "Raqamni yuboring:")

@client.on(events.NewMessage(chats='me', pattern=r'^[1-4]$'))
async def select_variant(event):
    global selected_script, step
    selected_script = event.raw_text.strip()
    if selected_script == "1":
        step = "post_link"
        await event.respond("📨 Post linkini forward qiling yoki link tashlang:")
    elif selected_script == "2":
        step = "channel_input"
        await event.respond("📨 Kanal postini forward qiling yoki link yuboring:")
    elif selected_script == "3":
        step = "group_input"
        await event.respond("📨 Kanalni yuboring (chatga bog‘langan bo‘lishi kerak):")
    elif selected_script == "4":
        step = "join_target"
        await event.respond("📥 Kanal yoki guruh linkini yuboring (barcha akkauntlar qo‘shiladi):")

@client.on(events.NewMessage(chats='me'))
async def step_handler(event):
    global step, forwarded_channel, trigger_text, reply_texts, post_id

    if selected_script == "1" and step == "post_link":
        if event.message.forward and event.message.forward.chat:
            forwarded_channel = event.message.forward.chat
            post_id = event.message.forward.channel_post
        else:
            match = re.match(r'https://t\.me/([\w_]+)/(\d+)', event.raw_text.strip())
            if match:
                forwarded_channel = await client.get_entity(match.group(1))
                post_id = int(match.group(2))
            else:
                await event.respond("❌ Link xato.")
                return
        step = "replies"
        await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")

    elif selected_script in ("2", "3") and step in ("channel_input", "group_input"):
        fwd = event.message.forward
        entity = fwd.chat if fwd and fwd.chat else None
        if not entity:
            match = re.match(r'https://t\.me/([\w_]+)', event.raw_text.strip())
            if match:
                entity = await client.get_entity(match.group(1))
        if not entity:
            await event.respond("❌ Kanalni topib bo‘lmadi.")
            return

        if selected_script == "2":
            forwarded_channel = entity
            step = "trigger"
            await event.respond("🔑 Trigger so‘zini kiriting:")
        else:
            try:
                full = await client(GetFullChannelRequest(entity))
                if full.full_chat.linked_chat_id:
                    forwarded_channel = full.full_chat.linked_chat_id
                    step = "chat_replies"
                    await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")
                else:
                    await event.respond("❌ Kanalga chat ulangan emas.")
            except Exception as e:
                await event.respond(f"❌ Xatolik: {e}")

    elif selected_script == "2" and step == "trigger":
        trigger_text = event.raw_text.strip()
        step = "replies"
        await event.respond("📩 10 ta reply matnini yozing (har biri yangi qatorda):")

    elif selected_script == "4" and step == "join_target":
        match = re.match(r'https://t\.me/([\w_]+)', event.raw_text.strip())
        if not match:
            await event.respond("❌ Link xato.")
            return
        username = match.group(1)
        await event.respond("🔄 Kanal/guruhga qo‘shilmoqda...")
        await run_variant4_join(username)
        await event.respond("✅ Barcha akkauntlar qo‘shildi.")

    elif step in ("replies", "chat_replies"):
        reply_texts = [line.strip() for line in event.raw_text.splitlines() if line.strip()]
        if len(reply_texts) != 10:
            await event.respond("❌ Iltimos, aynan 10 ta reply yuboring.")
            return

        if selected_script == "1":
            await event.respond("✅ Replylar yuborilmoqda...")
            await run_variant1()
        elif selected_script == "2":
            await event.respond("✅ Trigger monitoring boshlandi.")
            await run_variant2_monitor()
        elif selected_script == "3":
            await event.respond("✅ Chatga xabar yuborilyapti...")
            await run_variant3_chat()

# === Variant 1 ===
async def run_variant1():
    await asyncio.gather(*[c.start() for c in clients])

    async def send_reply_task(i):
        try:
            channel = await clients[i].get_entity(forwarded_channel)
            result = await clients[i](GetDiscussionMessageRequest(peer=channel, msg_id=post_id))
            discussion_msg = next((m for m in result.messages if m.id != post_id), None)
            if discussion_msg:
                await clients[i].send_message(
                    entity=discussion_msg.to_id,
                    message=reply_texts[i],
                    reply_to=discussion_msg.id
                )
                print(f"[{i+1}] ✅ Reply yuborildi.")
            else:
                print(f"[{i+1}] ❌ Comment topilmadi.")
        except Exception as e:
            print(f"[{i+1}] ⚠️ Xatolik: {e}")

    await asyncio.gather(*[send_reply_task(i) for i in range(10)])

# === Variant 2 (Trigger bilan) ===
async def run_variant2_monitor():
    await asyncio.gather(*[c.start() for c in clients])

    @clients[0].on(events.NewMessage(chats=forwarded_channel.username if hasattr(forwarded_channel, 'username') else forwarded_channel.id))
    async def listen(event):
        msg = event.message
        if msg.text and trigger_text.lower() in msg.text.lower():
            print("✅ Trigger topildi:", msg.text)
            await asyncio.gather(*[
                retry_send_reply(clients[i], msg.id, reply_texts[i], i + 1)
                for i in range(10)
            ])

    print("📡 Trigger kuzatuv boshlandi")
    await clients[0].run_until_disconnected()

# === Retry bilan reply ===
async def retry_send_reply(client, msg_id, reply_text, number):
    retries = 0
    while True:
        try:
            channel = await client.get_entity(forwarded_channel)
            result = await client(GetDiscussionMessageRequest(peer=channel, msg_id=msg_id))
            discussion_msg = next((m for m in result.messages if m.id != msg_id), None)
            if discussion_msg:
                await client.send_message(
                    entity=discussion_msg.to_id,
                    message=reply_text,
                    reply_to=discussion_msg.id
                )
                print(f"[{number}] ✅ Reply yuborildi.")
                break
            else:
                print(f"[{number}] ❌ Comment topilmadi.")
                break
        except Exception as e:
            retries += 1
            print(f"[{number}] ⚠️ Qayta urinilmoqda ({retries}): {e}")
            await asyncio.sleep(0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001)

# === Variant 3 ===
async def run_variant3_chat():
    await asyncio.gather(*[c.start() for c in clients])

    async def send_chat_message(i):
        retries = 0
        while True:
            try:
                await clients[i].send_message(forwarded_channel, reply_texts[i])
                print(f"[{i+1}] ✅ Chatga yuborildi.")
                break
            except Exception as e:
                retries += 1
                print(f"[{i+1}] ❌ Qayta urinilmoqda ({retries}): {e}")
                await asyncio.sleep(0.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001)

    await asyncio.gather(*[send_chat_message(i) for i in range(10)])

# === Variant 4 ===
async def run_variant4_join(username):
    await asyncio.gather(*[c.start() for c in clients])

    async def join_task(i):
        try:
            entity = await clients[i].get_entity(username)
            await clients[i](JoinChannelRequest(channel=entity))
            print(f"[{i+1}] ✅ Kanalga qo‘shildi: {username}")

            # Ulangan chatni ham topamiz
            full = await clients[i](GetFullChannelRequest(entity))
            if full.full_chat.linked_chat_id:
                group = await clients[i].get_entity(full.full_chat.linked_chat_id)
                await clients[i](JoinChannelRequest(channel=group))
                print(f"[{i+1}] ✅ Chatga ham qo‘shildi.")
        except Exception as e:
            print(f"[{i+1}] ⚠️ Xatolik: {e}")

    await asyncio.gather(*[join_task(i) for i in range(10)])

# === Start ===
async def main():
    await client.start()
    print("🤖 Jasur bot tayyor")
    await client.run_until_disconnected()

asyncio.run(main())
