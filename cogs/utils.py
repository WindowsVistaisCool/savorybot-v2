import cogs
import json
import functools
import discord
import datetime, time
from typing import Union

# JSON R/W
def store(file, key=None, read=False, val=None, *, pop=False):
    with open(file, 'r') as v:
        x = json.load(v)
    if x is None: return
    if read is not False:
        if key is None:
            return x
        else:
            return x[key]
    elif pop is True:
            return
    else:
        if val is None:
            with open(file, 'w') as v:
                json.dump(key, v, indent=4)
            return
        x[key] = val
        with open(file, 'w') as v:
            json.dump(x, v, indent=4)

config = store('config.json', None, True)
guildID = config['slashGuildID']
rtVars = {}

# Cog utils (loading/set status)
async def get_ready(bot) -> None:
    global starttime
    starttime = time.time()
    config = store('config.json', None, True)
    for key, val in config['rtInit'].items(): rtVars[key] = val
    __show_warns(config)
    await __load_cogs(bot, config)
    if config["doAutomaticSync"]: await sync_commands(bot, config) # syncs commands to guilds or globally
    await __ready_status(bot, config['activity'])
    print("Ready")

def __show_warns(current_conf) -> None:
    warns = ""
    if current_conf['debug']['enabled']:
        warns += "WARNING: Debug mode is active!\n"
    if current_conf['loadedCogs'] == []:
        warns += "WARNING: No cogs are specified in to load!\n"
    if current_conf['ownerIDs'] == []:
        warns += "WARNING: Owner IDs are unset!\n"
    warns = warns[:-2]
    if warns != "":
        print(f"\033[9{'3m' + warns}\033[0m")

# Internal method to fetch cogs and call their setup() function
async def __load_cogs(bot: discord.ext.commands.Bot, config) -> None:
    for cog in config['loadedCogs']:
        await bot.load_extension(cog)

# Internal method for syncing commands to a guild (or globally)
async def sync_commands(bot: discord.ext.commands.Bot, config: dict) -> None:
    await bot.tree.sync(guild=discord.Object(id=config['slashGuildID']) if config['slashGuildID'] is not None else None)

# Internal method for setting status
# TODO: This function was written a LONG time ago. Some variable names are... very indescriptive.
async def __ready_status(client: Union[discord.Client, discord.ext.commands.Bot], activityData: dict) -> None:
    def type():
        activityName = activityData['name']
        if activityData['type'].startswith('l'):
            return discord.Activity(type=discord.ActivityType.listening, name=activityName)
        elif activityData['type'].startswith('w'):
            return discord.Activity(type=discord.ActivityType.watching, name=activityName)
        elif activityData['type'].startswith('c'):
            return discord.Activity(type=discord.ActivityType.competing, name=activityName)
        elif activityData['type'].startswith('s'):
            return discord.Streaming(name=activityName, url=activityData['streamURL'])
        elif activityData['type'].startswith('p'):
            return disclrd.Game(name=activityName)
        else:
            return None
    def stat():
        status = activityData['status']
        if status == 'dnd':
            return discord.Status.dnd
        elif status == 'invisible':
            return discord.Status.invisible
        elif status == 'idle':
            return discord.Status.idle
        else:
            return discord.Status.online
    if activityData['type'] != 'n':
        await client.change_presence(status=stat(), activity=type())

# Returns current uptime
def get_uptime() -> str:
    return str(datetime.timedelta(seconds=int(round(time.time()-starttime))))

# Returns current runtime vars
def get_rt_vars() -> dict:
    return rtVars

# Changes a specific runtime var
def change_rt_var(key: str, val: str) -> dict:
    rtVars[key] = val
    return rtVars

# puts a new rt for runtime vars
def put_rt(data: dict) -> dict:
    rtVars = data
    return rtVars

# Returns current configuration (only)
def get_config() -> dict:
    return config

# Set config with whole JSON object
def set_config(json: dict) -> dict:
    store('config.json', json)
    config = store('config.json', None, True)
    return config

class buttons:
    class Trash(discord.ui.Button):
        def __init__(self, row=1, *, style=discord.ButtonStyle.danger, emoji="🗑️"):
            super().__init__(custom_id="presets:trash", row=row, style=style, emoji=emoji)
        
        async def callback(self, interaction: discord.Interaction): pass

class debug:
    DEBUG_ENABLED = get_config()['debug']['enabled'] # dynamic
    STRING_DEFAULT = "**Debug mode is enabled!**"

    # Functions
    @staticmethod
    def debugText(text: str = STRING_DEFAULT) -> str:
        return text if debug.DEBUG_ENABLED else ""

    @classmethod
    def isEnabled(cls) -> bool:
        return cls.DEBUG_ENABLED

    # Decorators
    @classmethod
    def fail_if_debug(cls) -> callable:
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if cls.DEBUG_ENABLED:
                    await args[1].channel.send(f"**ERR**: `{args[1].author}` tried invoking `{func.__name__}`, but debug mode is enabled!")
                else:
                    return await func(*args, **kwargs)
            return wrapped
        return wrapper
    
    @classmethod
    def warn_if_debug(cls) -> callable:
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if cls.DEBUG_ENABLED:
                    await args[1].channel.send(f"*WARN*: Debug mode is currently enabled! Some features may not work properly.")
                return await func(*args, **kwargs)
            return wrapped
        return wrapper
    
    @classmethod
    def fail_debug_only(cls) -> callable:
        def wrapper(func):
            @functools.wraps(func)
            async def wrapped(*args, **kwargs):
                if not cls.DEBUG_ENABLED:
                    await args[1].chnanel.send(f"**ERR**: `{args[1].author}` tried invoking `{func.__name__}`, but debug mode is disabled!")
                else:
                    return await func(*args, **kwargs)
            return wrapped
        return wrapper