import asyncio
from pyrogram import Client, filters
from database.guncelTarih import guncelTarih
from info import AUTH_CHANNEL, LOG_CHANNEL, YOU_JOINED
from pyrogram.types import ChatMemberUpdated

from utils import temp

@Client.on_chat_member_updated(filters.chat(AUTH_CHANNEL))
async def user_accepted(bot:Client, cmu: ChatMemberUpdated):
    if not cmu.new_chat_member: return
    if cmu.new_chat_member.user.is_bot: return
    yeni = cmu.new_chat_member.user
    if YOU_JOINED:
        await bot.send_message(yeni.id, "Kanala katıldın. Şimdi beni kullanabilirsin.")
        await asyncio.sleep(1)
    await bot.send_message(LOG_CHANNEL,
        f"#{temp.U_NAME}"
        "\n#YeniKatılım" + \
        f"\n\nAd: `{yeni.first_name}`" + \
        f"\nSoyad: `{yeni.last_name}`" + \
        f"\nKullanıcı Adı: @{yeni.username}" + \
        f"\nID: `{yeni.id}`" + \
        f"\nEtiket: {yeni.mention}" + \
        f"\nDC: `{yeni.dc_id}`" + \
        f"\nDil: `{yeni.language_code}`" + \
        f"\nLink: tg://user?id={str(yeni.id)}" + \
        f"\nTarih: {guncelTarih()}"
    )
