import logging
logger = logging.getLogger(__name__)
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, SUPPORT_CHAT
from database.users_chats_db import db
from utils import temp
from pyrogram.errors import ChatAdminRequired

# https://t.me/GetTGLink/4179
@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        if not SUPPORT_CHAT: reply_markup = None
        else: reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]])
        
        await bot.send_message(
            chat_id=chat,
            text='Bu sohbeti sahibim yasaklamış. Elveda.',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply_text('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply_text("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply_text(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply_text('Chat Succesfully Disabled')
    try:
        if not SUPPORT_CHAT: reply_markup = None
        else: reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]])
        await bot.send_message(
            chat_id=chat_,
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply_text(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply_text('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply_text("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply_text('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply_text("Chat Succesfully re-enabled")


# a function for trespassing into others groups, Inspired by a Vazha
# Not to be used , But Just to showcase his vazhatharam.
@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot:Client, message:Message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    chat = message.command[1]
    try: chat = int(chat)
    except: return await message.reply_text('Give Me A Valid Chat ID')
    try: gruplink = await bot.create_chat_invite_link(chat)
    except: gruplink = None
    try: silebilir = (await bot.get_chat_member(chat, temp.ME)).privileges.can_delete_messages
    except: silebilir = False
    if gruplink:
        tosend = f"#{temp.U_NAME}" \
        "\n#YeniLink" \
        f"\n\nLink: {gruplink.invite_link}" \
        f"\nTarih: {gruplink.date}" \
        f"\nSilebilir: {str(silebilir)}"
        await message.reply_text(tosend, quote=True)


@Client.on_message(filters.command('izinler') & filters.user(ADMINS))
async def get_privileges(bot:Client, message:Message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    chat = message.command[1]
    try: chat = int(chat)
    except: return await message.reply_text('Give Me A Valid Chat ID')
    try: silebilir = (await bot.get_chat_member(chat, temp.ME)).privileges
    except: silebilir = False
    try: cet = await bot.get_chat(chat)
    except: cet = ''
    if silebilir:
        tosend = f"#{temp.U_NAME}" \
        "\n#YeniIzinListesi" \
        f"\n\nİzinlerim:\n\n{str(silebilir)}" \
        f"\n\nÇet:\n\n{str(cet)}"
        await message.reply_text(tosend, quote=True)



@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply_text('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply_text("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply_text("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply_text(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply_text(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply_text(f"Succesfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply_text("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply_text("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply_text(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply_text(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply_text(f"Succesfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply_text('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply_text('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")
