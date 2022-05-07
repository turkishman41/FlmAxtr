import logging
from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from info import ADMINS, AUTH_CHANNEL, BROADCAST_AS_COPY
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def broadcast_messages(bot, user_id, message):
    if AUTH_CHANNEL:
        try:
            user = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        except UserNotParticipant:
            return False, "Blocked"
        except Exception as e:
            logging.exception(e)
        else:
            if user.status == ChatMemberStatus.BANNED:
                return False, "Blocked"
    try:
        if BROADCAST_AS_COPY is False:
            await message.forward(chat_id=user_id)
        elif BROADCAST_AS_COPY is True:
            await message.copy(chat_id=user_id, protect_content=True)
        return True, "Succes"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(bot, user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Hesap silindiği için veritabanından kaldırıldı.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} - Bot'u engelledi.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Kimliği geçersiz")
        return False, "Error"
    except Exception as e:
        return False, "Error"


@Client.on_message(filters.command("yay") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='Mesajı yayınlıyorum')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0
    async for user in users:
        pti, sh = await broadcast_messages(bot, int(user['id']), b_msg)
        if pti:
            success += 1
        elif not pti:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(
                f"Broadcast in progress:\n\n"
                f"Total Users {total_users}\n"
                f"Completed: {done} / {total_users}\n"
                f"Success: {success}\n"
                f"Blocked: {blocked}\n"
                f"Deleted: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"Broadcast Completed:\n"
        f"Completed in {time_taken} seconds.\n\n"
        f"Total Users {total_users}\n"
        f"Completed: {done} / {total_users}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}")
