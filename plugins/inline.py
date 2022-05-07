import logging
from urllib.parse import quote
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import CallbackQuery
from database.ia_filterdb import get_search_results
from database.temizleyici import cleanhtml
from utils import is_subscribed, get_size
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CAPTION_SPLITTER, \
    CUSTOM_FILE_CAPTION, BUTTON_COUNT, JOIN_CHANNEL_WARNING, SEND_WITH_BUTTONS, SHARE_BUTTON_TEXT
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME


def get_reply_markup(username, query):
    if not SEND_WITH_BUTTONS: return None
    url = 't.me/share/url?url=' + quote(SHARE_BUTTON_TEXT.format(username=username))
    buttons = [[
        InlineKeyboardButton('Tekrar Ara', switch_inline_query_current_chat=query),
        InlineKeyboardButton('Botu Paylaş', url=url)
        ]]
    return InlineKeyboardMarkup(buttons)


@Client.on_inline_query(filters.user(AUTH_USERS) if AUTH_USERS else None)
async def answer(bot:Client, query:CallbackQuery):
    # kanala katıldı mı?
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        if JOIN_CHANNEL_WARNING:
            await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='Botu kullanmak için kanalıma abone olmalısınız.',
                           switch_pm_parameter="subscribe")
        return
    results = []
    if '|' in query.query:
        text, file_type = query.query.split('|', maxsplit=1)
        text = text.strip()
        file_type = file_type.strip().lower()
    else:
        text = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(bot.username, query=text)
    files, next_offset, total = await get_search_results(text,
                                                         file_type=file_type,
                                                         max_results=BUTTON_COUNT,
                                                         offset=offset)

    for file in files:
        f_caption = file.caption
        if not f_caption: f_caption = str(file.file_name)
        f_caption += '' if CUSTOM_FILE_CAPTION is None else f'\n{CUSTOM_FILE_CAPTION}'

        altmetin = f'Boyut: {get_size(file.file_size)}, Tür: {file.file_type}'
        try:
            inlinecaption = cleanhtml(file.caption.replace('\n', ' '))
        except:
            inlinecaption = None
        if inlinecaption: altmetin += f'{CAPTION_SPLITTER}{inlinecaption}'

        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                document_file_id=file.file_id,
                caption=f_caption,
                description=altmetin,
                reply_markup=reply_markup))

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} {total} Sonuç Bulundu"
        if text:
            switch_pm_text += f": {text}"
        try:
            await query.answer(results=results,
                               is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=switch_pm_text,
                               switch_pm_parameter="start",
                               next_offset=str(next_offset))
        except QueryIdInvalid:
            pass
        except Exception as e:
            logging.exception(str(e))
            await query.answer(results=[], is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=str(e)[:63],
                               switch_pm_parameter="error")
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} Sonuç yok'
        if text:
            switch_pm_text += f': "{text}"'

        await query.answer(results=[],
                           is_personal=True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")
