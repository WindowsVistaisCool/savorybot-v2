import discord
from discord.ext import commands
from cogs.utils import debug, config

# Interaction cog imports
from cogs.applications import Applications
from cogs.suggestions import Suggestions
from cogs.polls import Polls
from cogs.tictactoe import Tictactoe

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try: interaction.data["custom_id"]
        except: return
        if interaction.data["custom_id"] == "presets:trash":
            await interaction.message.delete()
        elif interaction.data["custom_id"].startswith('bot::refresh'):
            callbackID = interaction.data["custom_id"].split('-')[1]
            if callbackID == 'fragappmods':
                userID = int(interaction.message.embeds[0].footer.text)
                view = Applications.views.FragAppMods()
                view.setID(userID)
                await interaction.message.edit(view=view)
            await interaction.response.defer()
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
        elif interaction.data["custom_id"].startswith("bot::fragapp"):
            await Applications.event_callback(interaction)
        elif interaction.data["custom_id"].startswith("bot::sgst"):
            await Suggestions.event_callback(interaction)
        elif interaction.data["custom_id"].startswith("bot::poll"):
            await Polls.event_callback(interaction)
        elif interaction.data["custom_id"].startswith("bot::tictactoe"):
            await Tictactoe.event_callback(interaction)

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