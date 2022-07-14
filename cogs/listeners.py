import discord
from discord.ext import commands
from cogs.utils import debug, config

# Interaction cog imports
from cogs.applications import Applications

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try: interaction.data["custom_id"]
        except: return
        if interaction.data["custom_id"] == "presets:trash":
            await interaction.message.delete()
        elif interaction.data["custom_id"] == "bot::verify":
            await interaction.response.defer()
            verifyRole = interaction.guild.get_role(config["snowflakes"]["verifyRole"])
            lockedRole = interaction.guild.get_role(config["snowflakes"]["lockedRole"])
            await interaction.user.add_roles(verifyRole)
            await interaction.user.remove_roles(lockedRole)
        elif interaction.data["custom_id"] == "bot::apply":
            modal = Applications.modals.Apply()
            modal.supply_cog(Applications)
            await interaction.response.send_modal(modal)

    # @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if ctx.channel.id != 788889735157907487 or ctx.author.id != 159985870458322944: return

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