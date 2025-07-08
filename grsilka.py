from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, SendMessageRequest
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
import asyncio

# Akkaunt ma'lumotlari
accounts = [
   
    {
        "api_id": 27996139,
        "api_hash": '8057566b4d48b75b351a2979d20171b0',
        "session": 'maxmudovku'
    },
   
]

# Guruh taklif havolasi
private_invite_link = ' https://t.me/+autosmss'  # misol uchun: https://t.me/+autosmss

# Har bir akkaunt uchun alohida xabar
custom_texts = {
    
    'maxmudovku': "2",
    
}

async def join_and_send_id(client, link, session_name, custom_text):
    try:
        if '+' in link:
            hash_part = link.split("+")[-1]

            # Guruhga qo‘shilish
            chat = await client(ImportChatInviteRequest(hash_part))
            entity = chat.chats[0]
            chat_id = entity.id
            title = entity.title

            print(f"[{session_name}] ✅ Guruhga qo‘shildim: {title} (ID: {chat_id})")

            # Xabar yuborish
            full_message = f"{custom_text}\n\nGuruh ID: `{chat_id}`"
            await client(SendMessageRequest(
                peer=entity,
                message=full_message,
                parse_mode='markdown'
            ))
            print(f"[{session_name}] 📩 Xabar yuborildi.")

        else:
            print(f"[{session_name}] ❌ Link noto‘g‘ri formatda.")
    except UserAlreadyParticipantError:
        print(f"[{session_name}] ℹ️ Allaqachon guruhdasiz.")
    except Exception as e:
        print(f"[{session_name}] ❌ Xatolik: {e}")

async def main():
    clients = []
    for acc in accounts:
        client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
        await client.start()
        clients.append((client, acc["session"]))

    tasks = [
        join_and_send_id(client, private_invite_link, session, custom_texts.get(session, "Salom, guruhga qo‘shildim."))
        for client, session in clients
    ]
    await asyncio.gather(*tasks)

    for client, _ in clients:
        await client.disconnect()

asyncio.run(main())
