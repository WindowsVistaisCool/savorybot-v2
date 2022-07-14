import discord
from discord.ext import commands
from cogs.utils import debug

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"That command was not found! {debug.debugText()}", delete_after=4)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"You do not have permission! {debug.debugText()}", delete_after=4)
        else:
            await ctx.send(f"Unkown error: {error} {debug.debugText('| ' + debug.STRING_DEFAULT)}")
    
async def setup(bot):
    await bot.add_cog(Listeners(bot))