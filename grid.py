from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
import asyncio

# 1-akkaunt
api_id1 = 29381099
api_hash1 = 'd03a2742fc1a23d7d520fc4412dd9851'
session1 = 'jasurn6'

# 2-akkaunt
api_id2 = 27996139
api_hash2 = '8057566b4d48b75b351a2979d20171b0'
session2 = 'maxmudovku'

# 3-akkaunt
api_id3 = 27890211
api_hash3 = 'b6edf9b6b68185c9b018e4263c9980bc'
session3 = 'halol_bolamen'

# 4-akkaunt
api_id4 = 21266546
api_hash4 = 'add6e254faf19039cc2db89b495999bb'
session4 = 'maxmudovk'

# 5-akkaunt
api_id5 = 25924006
api_hash5 = '8f237939099b8f2f817fb1471595525b'
session5 = 'soqqa_topuvchi'

# Kanal username
channel_username = 'autosmsss'

# Faqat shu matn bo‘lsa reply bo‘ladi
trigger_text = "ID"

# Reply matnlari
reply1 = "1302893185"
reply2 = "1302852813"
reply3 = "1302893477"
reply4 = "1302851981"
reply5 = "1302893809"

# Clientlar
client1 = TelegramClient(session1, api_id1, api_hash1)
client2 = TelegramClient(session2, api_id2, api_hash2)
client3 = TelegramClient(session3, api_id3, api_hash3)
client4 = TelegramClient(session4, api_id4, api_hash4)
client5 = TelegramClient(session5, api_id5, api_hash5)

async def try_send_reply(client, msg_id, reply_text, client_number, retries=5, delay=0.5):
    try:
        channel = await client.get_entity(channel_username)

        for attempt in range(retries):
            try:
                result = await client(GetDiscussionMessageRequest(
                    peer=channel,
                    msg_id=msg_id
                ))

                discussion_msg = None
                for m in result.messages:
                    if m.id != msg_id:
                        discussion_msg = m
                        break

                if discussion_msg:
                    await client.send_message(
                        entity=discussion_msg.to_id,
                        message=reply_text,
                        reply_to=discussion_msg.id
                    )
                    print(f"[{client_number}] ✅ Reply #{attempt+1}da yuborildi.")
                    return
                else:
                    print(f"[{client_number}] ⏳ {attempt+1}/5: comment hali yo'q.")
            except Exception as e:
                print(f"[{client_number}] ⚠️ Urinish {attempt+1}: {e}")

            await asyncio.sleep(delay)

        print(f"[{client_number}] ❌ {retries} marta urinildi, comment topilmadi.")

    except Exception as e:
        print(f"[{client_number}] ❌ Umumiy xatolik: {e}")

async def handle_post(event):
    msg = event.message
    if msg.text and trigger_text.lower() in msg.text.lower():
        print(f"🔍 Mos post: {msg.text}")
        await asyncio.gather(
            try_send_reply(client1, msg.id, reply1, 1),
            try_send_reply(client2, msg.id, reply2, 2),
            try_send_reply(client3, msg.id, reply3, 3),
            try_send_reply(client4, msg.id, reply4, 4),
            try_send_reply(client5, msg.id, reply5, 5),
        )
    else:
        print(f"⛔️ Mos emas: {msg.text}")

@client1.on(events.NewMessage(chats=channel_username))
async def channel_post(event):
    await handle_post(event)

@client2.on(events.NewMessage(chats=channel_username))
async def ignore_client2(event):
    pass

@client3.on(events.NewMessage(chats=channel_username))
async def ignore_client3(event):
    pass

@client4.on(events.NewMessage(chats=channel_username))
async def ignore_client4(event):
    pass

@client5.on(events.NewMessage(chats=channel_username))
async def ignore_client5(event):
    pass

async def main():
    await client1.start()
    await client2.start()
    await client3.start()
    await client4.start()
    await client5.start()
    print("🤖 Botlar 5ta akkaunt bilan ishlamoqda, kuzatmoqda...")
    await asyncio.gather(
        client1.run_until_disconnected(),
        client2.run_until_disconnected(),
        client3.run_until_disconnected(),
        client4.run_until_disconnected(),
        client5.run_until_disconnected()
    )

asyncio.run(main())