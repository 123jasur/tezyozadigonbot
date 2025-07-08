from telethon import TelegramClient, events
import asyncio
import re
from PIL import Image
import pytesseract
import io

# === Tesseract EXE joylashgan manzilni ko‘rsatish (Windows) ===
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# === 1-akkaunt ma'lumotlari ===
api_id1 = 29381099
api_hash1 = 'd03a2742fc1a23d7d520fc4412dd9851'
session1 = 'jasurn6'

# === 2-akkaunt ma'lumotlari ===


# === Kuzatiladigan kanal va yuboriladigan bot ===
source_channel = '@clazerup'
destination_bot = '@send'

# === Clientlarni yaratish ===
client1 = TelegramClient(session1, api_id1, api_hash1)


# === Belgini almashtirish funksiyasi ===
def replace_placeholder_or_default(text):
    """
    Agar 'Вместо <belgi> - <qiymat>' bo‘lsa:
        <belgi> ni <qiymat> bilan almashtiradi.
    Agar 'Вместо' bo‘lmasa:
        $ belgilarni avtomatik 3333 bilan almashtiradi.
    """
    placeholder_match = re.search(r'Вместо\s+(.)\s*-\s*(\S+)', text, re.IGNORECASE)
    if placeholder_match:
        symbol_to_replace = placeholder_match.group(1)  # Masalan: $
        replacement_value = placeholder_match.group(2)  # Masalan: 3333
        print(f"🔄 '{symbol_to_replace}' belgisi o‘rniga '{replacement_value}' qo‘yiladi.")

        # "Вместо ..." qatorini olib tashlash
        cleaned_text = re.sub(r'\n?Вместо\s+.\s*-\s*\S+', '', text, flags=re.IGNORECASE).strip()

        # Belgini almashtirish
        replaced_text = cleaned_text.replace(symbol_to_replace, replacement_value)
        return replaced_text
    else:
        # Agar 'Вместо' bo‘lmasa, $ belgilarni avtomatik 3333 bilan almashtirish
        if '$' in text:
            replaced_text = text.replace('$', '3333')
            print(f"⚙️ 'Вместо' topilmadi. '$' belgilar o‘rniga 3333 qo‘yildi.")
            return replaced_text.strip()
        return text.strip()

# === Rasmdan matn ajratish (OCR) ===
async def extract_text_from_image(event):
    try:
        file_bytes = await event.download_media(bytes)
        image = Image.open(io.BytesIO(file_bytes))

        # Oq-qora ga o‘tkazish
        image = image.convert('L')

        # Kontrastni oshirish
        image = image.point(lambda x: 0 if x < 160 else 255, '1')

        # OCR orqali matnni olish
        text = pytesseract.image_to_string(image, lang='eng+rus', config='--psm 6').strip()
        print(f"📷 OCR orqali o'qilgan matn:\n{text}")

        # Har bir qatorni tekshirish
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if re.fullmatch(r'[\w&$\/\\]{4,}', line):
                return line

    except Exception as e:
        print(f"❌ OCR xatolik: {e}")
    return None

# === Xabarni qayta ishlash funksiyasi ===
async def handle_message(client_name, event):
    text = event.message.message
    photo = event.message.photo

    # 1️⃣ Matndagi belgilarni almashtirish
    if text:
        final_text = replace_placeholder_or_default(text)
        if final_text:
            try:
                entity = await event.client.get_entity(destination_bot)
                await event.client.send_message(entity, final_text)
                print(f"[{client_name}] ✅ Xabar yuborildi: {final_text}")
                return
            except Exception as e:
                print(f"[{client_name}] ❌ Xabar yuborishda xatolik: {e}")

    # 2️⃣ Agar matn bo‘lmasa, rasmni o‘qish
    if photo:
        ocr_text = await extract_text_from_image(event)
        if ocr_text:
            try:
                entity = await event.client.get_entity(destination_bot)
                await event.client.send_message(entity, ocr_text)
                print(f"[{client_name}] ✅ Rasm matni yuborildi: {ocr_text}")
            except Exception as e:
                print(f"[{client_name}] ❌ Rasm matni yuborishda xatolik: {e}")
        else:
            print(f"[{client_name}] ⚠️ Rasm ichida matn topilmadi.")

# === Client1 uchun listener ===
@client1.on(events.NewMessage(chats=source_channel))
async def client1_handler(event):
    await handle_message("Client1", event)

# === Client2 uchun listener ===


# === Asosiy ishga tushirish ===
async def main():
    try:
        await client1.start()
        
        me1 = await client1.get_me()
        
        
        print("🔎 Kanalni kuzatyapti...")
        await asyncio.gather(
            client1.run_until_disconnected(),
            
        )
    except Exception as e:
        print(f"❌ Botni ishga tushirishda xatolik: {e}")

if __name__ == "__main__":
    asyncio.run(main())
