import os
import logging
import asyncio
from pyrogram.types.messages_and_media.message import Message
from database.filters_mdb import delete_all_files, delete_all_groups, delete_all_users
from database.guncelTarih import guncelTarih
from database.yardimMesajlari import yardimMesaji
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant 
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode, ChatType, MessageMediaType
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, FILE_PROTECTED, GEN_CHAT_LINK_DELAY, JOIN_CHANNEL_WARNING, LOG_CHANNEL, START_TXT, REQUEST_LINK, PICS
from database.users_chats_db import db
from utils import is_subscribed, temp
logger = logging.getLogger(__name__)

@Client.on_message(~filters.channel & filters.command(["start", "help", "h", "y", "yardım", "yardim", "stats"]))
async def start(client: Client, message: Message):
    try:
        forcsub = await client.create_chat_invite_link(AUTH_CHANNEL, creates_join_request=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return
    try:
        user = await client.get_chat_member(AUTH_CHANNEL, message.from_user.id)
        if user.status == ChatMemberStatus.BANNED:
            await client.delete_messages(
                chat_id=message.from_user.id,
                message_id=message.from_message.id,
                revoke=True,
                parse_mode=ParseMode.HTML
            )
            return
    except UserNotParticipant:
        await client.send_message(
            chat_id=message.from_user.id,
            text="Merhaba bu botu sadece gruba üye olanlar kullanabilir eğer gruba üye olmak istiyorsan aşağıdaki butondan istek gönder eğer fake isim koyarsan yada profil fotoğrafını yoksa seni gruba kabul edemem!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Kanalım", url=forcsub.invite_link)
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML, 
            protect_content=True
        )
        return
    # genel butonlar
    butonlar = [
            [
                InlineKeyboardButton('Ara 🔍', switch_inline_query_current_chat=''),
                InlineKeyboardButton('Bot Nasıl Kullanılır?', url='https://t.me/anagrupp2')
            ],
            [
                InlineKeyboardButton('Bot Destek', url=f"https://t.me/mmagneto"),
            ]
            ]
    # grup ?
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        reply_markup = InlineKeyboardMarkup(butonlar)
        await message.reply_text(
            chat_id=message.from_user.id,
            text=START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup, 
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonim"
            yeni = message.chat
            tosend = f"#{temp.U_NAME}" \
                "\n#YeniGrup" \
                f"\n\nAd: `{yeni.title}`" \
                f"\nKullanıcı Adı: @{yeni.username}" \
                f"\nID: `{yeni.id}`" \
                f"\nÜye: `{total}`" \
                f"\nEkleyen: {r_j} (`{message.from_user.id}`)" \
                f"\nDC: `{yeni.dc_id}`" \
                f"\nTarih: `{guncelTarih()}`"
            await db.add_chat(message.chat.id, message.chat.title)
            grubaeklendi = await client.send_message(LOG_CHANNEL, tosend)
            # grup linki ?s
            await asyncio.sleep(GEN_CHAT_LINK_DELAY*60)
            try: gruplink = await client.create_chat_invite_link(yeni.id)
            except: gruplink = None
            try: silebilir = (await client.get_chat_member(yeni.id,temp.ME)).privileges.can_delete_messages
            except: silebilir = False
            await asyncio.sleep(1)
            if gruplink:
                tosend = f"#{temp.U_NAME}" \
                "\n#YeniLink" \
                f"\n\nLink: {gruplink.invite_link}" \
                f"\nTarih: {gruplink.date}" \
                f"\nSilebilir: {str(silebilir)}"
                await grubaeklendi.reply_text(tosend, quote=True)
        return
    # kullanıcıyı dbye ekle
    if (not (message.from_user.id in ADMINS) and not \
    (await db.is_user_exist(message.from_user.id))):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        if LOG_CHANNEL:
            yeni = message.from_user
            await client.send_message(LOG_CHANNEL,
                f"#{temp.U_NAME}" \
                "\n#YeniKullanıcı" \
                f"\n\nAd: `{yeni.first_name}`" \
                f"\nSoyad: `{yeni.last_name}`" \
                f"\nKullanıcı Adı: @{yeni.username}" \
                f"\nID: `{yeni.id}`" \
                f"\nEtiket: {yeni.mention}" \
                f"\nDC: `{yeni.dc_id}`" \
                f"\nDil: `{yeni.language_code}`" \
                f"\nLink: tg://user?id={str(yeni.id)}" \
                f"\nTarih: `{guncelTarih()}`"
            )
    # normal start komutysa start texti gönder
    if len(message.command) != 2:
        reply_markup = InlineKeyboardMarkup(butonlar)
        return await message.reply_text(
                   chat_id=message.from_user.id,
                   text=START_TXT.format(message.from_user.mention),
                   reply_markup=reply_markup, 
                   parse_mode=ParseMode.HTML, 
                   disable_web_page_preview=True
               )  
    file_id = message.command[1]
    files_ = await get_file_details(file_id)
    if not files_:
        delo = await message.reply_text("Bulamadım bir şey.\nArama ipuçları için tıkla ve oku: /yardim")
        await asyncio.sleep(10)
        return await delo.delete()
    files = files_[0]
    f_caption = files.caption
    try:
        f_caption = files.caption
        if not f_caption: f_caption = str(files.file_name)
        f_caption += '' if CUSTOM_FILE_CAPTION is None else f'\n{CUSTOM_FILE_CAPTION}'
    except Exception as e:
        logger.exception(e)
        f_caption = f_caption
    ho = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=FILE_PROTECTED
    )
    await yardimMesaji(str(files.file_name), ho)

@Client.on_message(~filters.channel & filters.command('kanal') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **İndekslenen kanallar/gruplar**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Toplam:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply_text(text)
    else:
        file = 'İndekslenen kanallar.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(~filters.channel & filters.command('log') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('log.txt')
    except Exception as e:
        await message.reply_text(str(e))


@Client.on_message(~filters.channel & filters.command('sil') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if not (reply and reply.media):
        return await message.reply_text('Silmek istediğiniz dosyayı /sil ile yanıtlayın', quote=True)
    msg = await message.reply_text("İşleniyor...⏳", quote=True)
    for file_type in (MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO):
        media = getattr(reply, file_type.value, None)
        if media is not None:
            break
    else:
        return await msg.edit('Bu desteklenen bir dosya biçimi değil.')

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Dosya veritabanından başarıyla silindi.')
    else:
        # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39
        # have original file name.
        result = await Media.collection.delete_one({
            'file_name': media.file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('Dosya veritabanından başarıyla silindi.')
        else:
            await msg.edit('Veritabanında dosya bulunamadı.')


# admin paneli
@Client.on_message(~filters.channel & filters.command('admin') & filters.user(ADMINS))
async def adminpaneli(bot, message):
    await message.reply_text(
        'admin paneli',
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(text="admin", callback_data="help")
            ]]),
        quote=True)


@Client.on_message(~filters.channel & filters.regex(r'^\/deleteall+.*$') & filters.user(ADMINS))
async def delete_all_index(bot, message:Message):
    tayp = ''
    if message.text.lower() == '/deleteallfiles': tayp = 'Dosyalar'
    elif message.text.lower() == '/deleteallusers': tayp = 'Kullanıcılar'
    elif message.text.lower() == '/deleteallgroups': tayp = 'Gruplar'
    else: return

    await message.reply_text(
        f'Tüm {tayp.lower()} silinecek.\nDevam etmek istiyor musunuz?',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"Tüm {tayp}ı Sil", callback_data=f"deleteall#{tayp}")],
                [InlineKeyboardButton(text="İptal", callback_data="close_data")]
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^deleteall+.*$'))
async def delete_all_confirm(bot, query:CallbackQuery):
    nesilincek = query.data.split("#")[1]
    if nesilincek == 'Dosyalar':
        await delete_all_files(query.message)
    elif nesilincek == 'Kullanıcılar':
        await delete_all_users(query.message)
    elif nesilincek == 'Gruplar':
        await delete_all_groups(query.message)
    else:
        return query.message.edit(f'deleteall yaparken sorun çıktı ?')
    
