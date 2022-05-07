import logging
import logging.config
import os

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.INFO)
from platform import python_version
from pyrogram import Client, __version__
import pkg_resources
from pyrogram.raw.all import layer
from info import ADMINS, SESSION, API_ID, API_HASH, BOT_TOKEN
from utils import temp
logger = logging.getLogger(__name__)

def get_package_versions(file = 'requirements.txt'):
    toret = []
    file1 = open(file, 'r')
    lines = file1.readlines()
    file1.close()
    for line in lines:
        try:
            v = pkg_resources.get_distribution(line.strip()).version
        except Exception as e:
            logger.error(e)
            continue
        toret.append(f"{line.strip()}: {v}")
    return '\nPython Package Versions:\n\n' + '\n'.join(toret) + '\n'


class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        temp.info_bot_str = f"{me.username} ({me.id})" \
            f" - Python: {python_version()}" \
            f" - Pyrogram: {__version__}. Layer: {layer}" + \
            get_package_versions()
        logging.info(f"Started: {temp.info_bot_str}")
        if ADMINS != 0:
            try: await self.send_message(text="Doğdum.", chat_id=ADMINS[0])
            except Exception as t: logging.error(str(t))

    async def stop(self, *args):
        if ADMINS != 0:
            try: await self.send_message(text="Öldüm.", chat_id=ADMINS[0])
            except Exception as t: logging.error(str(t))
            await super().stop()
            logging.info(f"Stopped: {temp.info_bot_str}")

if os.path.isfile(SESSION + '.session'):
    try: os.remove(SESSION + '.session')
    except: pass

app = Bot()
app.run()
