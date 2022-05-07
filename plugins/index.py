import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import \
    ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.enums import MessageMediaType, ChatType
from database.guncelTarih import guncelTarih
from info import ADMINS, LOG_CHANNEL

from info import botStartTime
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from utils import temp
import re, time
from plugins.pm_filter import ReadableTime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

tg_link_regex = "(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user, fastordb = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'{chat} için indexlemeniz reddedildi.',
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process complete.', show_alert=True)
    msg = query.message

    await query.answer('İşleniyor...', show_alert=False)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'{chat} için indexlemeniz kabul edildi.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )
    try:
        chat = int(chat)
    except:
        chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot, fastordb == "dbindex")


@Client.on_message((filters.forwarded | ((filters.regex(tg_link_regex)) & filters.text)) & filters.private & filters.incoming)
async def send_for_index(bot:Client, message:Message):
    if message.text:
        regex = re.compile(tg_link_regex)
        match = regex.match(message.text)
        if not match:
            return await message.reply_text(
                'Ya son dosyanı gönder ya da son dosya linkini.' \
                '\nÖrnek: `https://t.me/c/648945648/616`' \
                '\nOlmadı yani bekleme burada boşuna.'
            )
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    try:
        cet = await bot.get_chat(chat_id)
    except (ChannelInvalid, ChannelPrivate):
        return await message.reply_text('Beni oraya yönetici olarak ekle ki görebileyim grubunu / kanalını')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply_text('Geçersiz kullanıcı adı.')
    except Exception as e:
        logger.exception(e)
        return await message.reply_text(f'Errors - {e}')
    if not cet: return await message.reply_text('Çet yok?')
    try: total_users = await bot.get_chat_members_count(chat_id)
    except: total_users = None
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply_text('Kanalın / Grubun gizliyse beni yönetici yapmalısın.')
    if k.empty:
        return await message.reply_text('Kanalın / Grubun gizliyse beni yönetici yapmalısın.')
    tosend = f"#{temp.U_NAME}" \
            "\n#YeniIndexleme" \
            f"\n\nSohbet Adı: `{cet.title}`" \
            f"\nSohbet KA: @{cet.username}" \
            f"\nSohbet Kimliği: `{cet.id}`" \
            f"\nSohbet Üyeleri: `{str(total_users)}`" \
            f"\nSohbet DC: `{cet.dc_id}`" \
            f"\n\nİndexleyen Adı: {message.from_user.mention} (`{message.from_user.id}`)" \
            f"\nİndexleyen Soyadı: `{message.from_user.last_name}`" + \
            f"\nİndexleyen Kimliği: @{message.from_user.username}" + \
            f"\nİndexleyen DC: `{message.from_user.dc_id}`" \
            f"\nİndexleyen Dil: `{message.from_user.language_code}`" \
            f"\nİndexleyen Link: tg://user?id={str(message.from_user.id)}" \
            f'\n\nBaş ID: {str(temp.CURRENT)}' \
            f'\nSon ID: `{last_msg_id}`' \
            f'\n\n5. mesajdan başla: `/setskip 5`' \
            f'\nDetaylar: `/izinler {cet.id}`' \
            f"\nTarih: `{guncelTarih()}`"
    if message.from_user.id in ADMINS:
        buttons = [
            [InlineKeyboardButton('Yes (DB)',
                                    callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#dbindex')
            ],
            [InlineKeyboardButton('Yes (Fast)',
                                    callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#fastindex')
            ],
            [InlineKeyboardButton('Reject Index', callback_data='close_data')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        return await message.reply_text(tosend, reply_markup=reply_markup)

    if type(chat_id) is int:
        try: link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply_text('Make sure iam an admin in the chat and have permission to invite users.')
    else: link = f"@{message.forward_from_chat.username}"

    buttons = [
        [
            InlineKeyboardButton('Yes (DB)',
                                callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#dbindex')
        ],
        [
            InlineKeyboardButton('Yes (Fast)',
                                callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#fastindex')
        ],
        [
            InlineKeyboardButton('Reject Index',
                                callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}#silme'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    tosend += f"\nLink: {link}"
    await bot.send_message(LOG_CHANNEL, tosend, reply_markup=reply_markup)
    await message.reply_text('Katkılarınız için teşekkürler. Moderatörlerimiz içeriğinizi inceledikten sonra size buradan dönüş yapacak.')

@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply_text("Bir sayı ver")
        await message.reply_text(f"{skip}. mesajdan itibaren kaydetmeye başlayacğım.")
        temp.CURRENT = int(skip)
    else:
        await message.reply_text("Bir sayı ver")


async def index_files_to_db(lst_msg_id, chat, msg, bot, dbindex):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    kayitdisi = 0
    starting = time.time()
    hiz = 0
    async with lock:
        try:
            total = lst_msg_id + 1
            current = temp.CURRENT
            temp.CANCEL = False
            while current < total:
                try:
                    message = await bot.get_messages(chat_id=chat, message_ids=current, replies=0)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    message = await bot.get_messages(
                        chat,
                        current,
                        replies=0
                    )
                except Exception as e:
                    logger.exception(e)
                try:
                    hiz = (current / ((time.time() - starting).__round__())).__round__()
                except:
                    hiz = 0
                if temp.CANCEL:
                    await msg.edit(f"Başarıyla İptal Edildi\n\n"
                                   f"`{total_files}` Dosya başarıyla kaydedildi!\n"
                                   f"Yinelenen Dosyalar Atlandı: `{duplicate}`\n"
                                   f"Silinen Mesajlar Atlandı: `{deleted}`\n"
                                   f"Medya Dışı Mesajlar Atlandı: `{no_media + unsupported}`(Unsupported Media - `{unsupported}` )\n"
                                   f"Es geçilenler: `{kayitdisi}`\n"
                                   f"Oluşan Hatalar: `{errors}`\n"
                                   f"Süre: `{ReadableTime(time.time() - starting)}`\nHız: `{hiz} öge/saniye`\n"
                                   f"Bot Ömrü: `{ReadableTime(time.time() - botStartTime)}`")
                    break
                current += 1
                # kaçta bir güncellesin
                kactabir = 20 if dbindex else 200
                if current % kactabir == 0:
                    reply = InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='index_cancel')]])
                    try:
                        await msg.edit_text(text=f"Starting ID: {str(temp.CURRENT)}\n"
                                                 f"Alınan toplam ileti sayısı: `{current}`\n"
                                                 f"Toplam mesaj kaydedildi: `{total_files}`\n"
                                                 f"Yinelenen Dosyalar Atlandı: `{duplicate}`\n"
                                                 f"Silinen Mesajlar Atlandı: `{deleted}`\n"
                                                 f"Medya Dışı Mesajlar Atlandı: `{no_media}`\n"
                                                 f"Desteklenmeyen Medya Atlandı: `{unsupported}`\n"
                                                 f"Oluşan Hatalar: `{errors}`\n"
                                                 f"Es geçilenler: `{kayitdisi}`\n"
                                                 f"Index from: `/setskip {current}`\n"
                                                 f"Süre: `{ReadableTime(time.time() - starting)}`\n"
                                                 f"Hız: `{hiz} öge/saniye`\n"
                                                 f"Bot Ömrü: `{ReadableTime(time.time() - botStartTime)}`",
                                            reply_markup=reply)
                    except:
                        pass
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [MessageMediaType.AUDIO, MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                if dbindex:
                    media.file_type = message.media.value
                    media.caption = message.caption
                    res = await save_file(media)
                    if res == 1:
                        total_files += 1
                    elif res == 2:
                        duplicate += 1
                    elif res == 3:
                        errors += 1
                    elif res == 4:
                        kayitdisi += 1
        except Exception as e:
            logger.exception(e)
            await msg.edit(f'Error: {e}')
        else:
            await msg.edit(f'`{total_files}` Dosya başarıyla kaydedildi!\n'
                           f'Yinelenen Dosyalar Atlandı: `{duplicate}`\n'
                           f'Silinen Mesajlar Atlandı: `{deleted}`\n'
                           f'Medya Dışı atlandı: `{no_media}`\n'
                           f'Desteklenmeyen Medya atlandı: `{unsupported}`\n'
                           f'Es geçilenler: `{kayitdisi}`\n'
                           f'Oluşan Hatalar: `{errors}`\n'
                           f'Süre: `{ReadableTime(time.time() - starting)}`\n'
                           f'Hız: `{hiz} öge/saniye`\n'
                           f'Bot Ömrü: `{ReadableTime(time.time() - botStartTime)}`')
