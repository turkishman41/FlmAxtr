from pyrogram.types import Message
from info import HELP_MESSAGES_AFTER_FILE

async def yardimMesaji(dosyaadi:str, message:Message):
    if not HELP_MESSAGES_AFTER_FILE: return
    # + 001 gibi arşivse tuto gönder
    if dosyaadi and dosyaadi.endswith(tuple(["00", "01", "02", "03", "04", "05"])):
        await message.reply_text(
            "Bölümlü arşiv tespit ettim (sanırım)\naçmak için şuna ihtiyacın olacak: " + \
            "https://telegra.ph/0-a%C3%A7mak-ve-olu%C5%9Fturmak-04-05\nrica ederim.",
            disable_web_page_preview=True, quote=True)
    # - 001 gibi arşivse tuto gönder

    # + 001 gibi arşivse tuto gönder
    elif dosyaadi and dosyaadi.endswith(tuple(["rar", "zip", "7z", "tar", "gz"])):
        await message.reply_text(
            "Arşiv tespit ettim (sanırım)\narşivleri telegram içinden çıkartmak için bazı botlar: @unziprobot " + \
            "@UnzipinBot @UnArchiveBot @ExtractProBot @ExtractorRobot",
            disable_web_page_preview=True, quote=True)
    # - 001 gibi arşivse tuto gönder

    # + 001 gibi arşivse tuto gönder
    elif dosyaadi and dosyaadi.endswith(tuple(["exe", "msi", "jar"])):
        await message.reply_text(
            "Program tespit ettim (sanırım)\nözellikle bu dosya türünde dikkatli olmalısın." + \
            "\nVirüs tarama botları: @VirusTotalAV_bot @VirusTotal_AVBot",
            disable_web_page_preview=True, quote=True)
    # - 001 gibi arşivse tuto gönder
