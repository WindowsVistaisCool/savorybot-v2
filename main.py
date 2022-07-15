from dotenv import dotenv_values
from discord import Intents
from discord.ext.commands import Bot
from cogs.utils import store, get_ready

config = store('config.json', None, True)
intents = Intents.default()
intents.message_content = True
intents.bans = True
intents.members = True
bot = Bot(
    command_prefix=config['prefix'],
    owner_ids=config['ownerIDs'],
    intents=intents
)

@bot.event
async def on_ready():
    await get_ready(bot)

try: bot.run(dotenv_values(".env")["TOKEN"])
except: print("\033[91mERROR: Token is not set!\033[0m")