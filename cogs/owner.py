import discord
from discord.ext import commands
from discord import app_commands, ui
from cogs import utils

# Eval command imports
import sys
import requests
import io
import cogs
from aioconsole import aexec
from asyncio import sleep
from datetime import datetime

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await utils.sync_commands(self.bot, utils.config)

    @commands.command()
    @commands.is_owner()
    async def r(self, ctx, cog: str = "owner"):
        await ctx.message.delete()
        try:
            await self.bot.reload_extension("cogs." + cog)
        except:
            await ctx.send("Failure reloading cog `" + cog + "`", delete_after=5)

    @commands.command()
    @commands.is_owner()
    async def nv(self, ctx):
        await ctx.message.delete()
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await message.edit(view=None)

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx, amount: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=int(amount))

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        out, err = io.StringIO(), io.StringIO()
        silence = False
        if code.startswith('-s'):
            silence = True
            code = code[3:]
            await ctx.message.delete()
        code = code[:-3]
        code = code[5:]
        args = {
            "discord": discord,
            "ui": ui,
            "ctx": ctx,
            "self": self,
            "cogs": cogs,
            "presets": cogs.embeds.presets,
            "sleep": sleep,
            "requests": requests,
            "datetime": datetime
        }
        sys.stdout = out
        sys.stderr = err
        await aexec(code, args) # main exec process
        results = out.getvalue()
        errors = err.getvalue()
        if not silence:
            pass#await ctx.send(f"```py\n{results}```{('```Errors: ' + errors + '```') if errors != '' else ''}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))