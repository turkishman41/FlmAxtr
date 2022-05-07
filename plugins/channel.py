from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from info import CHANNELS
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in (MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO):
        media = getattr(message, file_type.value, None)
        if media is not None: break
    else: return

    media.file_type = file_type.value
    media.caption = message.caption
    await save_file(media)
