import discord
from discord import app_commands
from discord.ext import commands
from cogs import utils
from typing import Optional

class Testing(commands.Cog):
    guildID = utils.guildID
    def __init__(self, bot):
        self.bot = bot

    class View(discord.ui.View):
        def __init__(self, user, timeout: Optional[float] = 60.0):
            super().__init__(timeout=timeout)
            self.values = None
            self.user = user
        
        @discord.ui.button(label="test", style=discord.ButtonStyle.primary, custom_id="tt")
        async def test_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user == self.user:
                await interaction.response.send_message("test!", ephemeral=True)
        
        async def on_timeout(self):
            pass

    @app_commands.command()
    @app_commands.guilds(discord.Object(id=guildID))
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message('Bonk', view=self.View(interaction.user))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Testing(bot))