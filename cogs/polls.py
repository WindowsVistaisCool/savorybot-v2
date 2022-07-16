import discord
from discord import ui, app_commands
from discord.ext import commands
from cogs import utils, checks
from typing import Literal
from datetime import datetime

class Polls(commands.Cog):
    guildID = utils.guildID
    def __init__(self, bot):
        self.bot = bot
    
    @classmethod
    async def event_callback(cls, interaction: discord.Interaction):
        pollID, pollChannel = [int(i) for i in interaction.data["custom_id"].split("-")[1:]]
        channel = interaction.guild.get_channel(pollChannel)
        message = await channel.fetch_message(pollID)
        if interaction.data['custom_id'].startswith("bot::poll::0"):
            if interaction.data['custom_id'].startswith("bot::poll::0::v"):
                embed = message.embeds[0]
                if interaction.user.mention in embed.fields[1].value:
                    await interaction.response.send_message("You cannot up/down vote again!", ephemeral=True)
                    return
                if interaction.data['custom_id'].startswith("bot::poll::0::vu"):
                    embed.set_field_at(0, name="Yes", value=f"***{int(embed.fields[0].value[3:-3]) + 1}***")
                else:
                    embed.set_field_at(1, name="No", value=f"***{int(embed.fields[1].value[3:-3]) + 1}***")
                embed.set_field_at(2, name="Participants", value=(embed.fields[2].value if embed.fields[2].value != 'None' else "") + f"{interaction.user.mention}", inline=False)
                await message.edit(embed=embed)
        await interaction.response.defer()

    class views:
        class YNPoll(ui.View):
            def __init__(self, cog, pollID, pollChannel):
                self.cog = cog
                self.pollID = pollID
                self.pollChannel = pollChannel
                super().__init__(timeout=None)
                self.add_item(self.b_upvote(self.pollID, self.pollChannel))
                self.add_item(self.b_downvote(self.pollID, self.pollChannel))
            
            class b_upvote(ui.Button):
                def __init__(self, pollID, pollChannel):
                    super().__init__(emoji="👍", style=discord.ButtonStyle.success, custom_id=f"bot::poll::0::vu-{pollID}-{pollChannel}")
                async def callback(self, interaction: discord.Interaction): pass
            
            class b_downvote(ui.Button):
                def __init__(self, pollID, pollChannel):
                    super().__init__(emoji="👎", style=discord.ButtonStyle.danger, custom_id=f"bot::poll::0::vd-{pollID}-{pollChannel}")
                async def callback(self, interaction: discord.Interaction): pass

    class modals:
        class YNInitiate(ui.Modal, title="Start a Y/N poll"):
            m_title = ui.TextInput(label="Poll Title", style=discord.TextStyle.paragraph, max_length=256)

            def supply_params(self, cog, channel) -> None:
                self.cog = cog
                self.channel = channel

            async def on_submit(self, interaction: discord.Interaction):
                embed = discord.Embed(title=interaction.data['components'][0]['components'][0]['value'], color=discord.Color.blurple(), timestamp=datetime.now())
                embed.set_footer(text="Started at")
                embed.add_field(name="Yes", value="***0***")
                embed.add_field(name="No", value="***0***")
                embed.add_field(name="Participants", value="None", inline=False)
                message = await self.channel.send(embed=embed)
                view = self.cog.views.YNPoll(self.cog, message.id, self.channel.id)
                await message.edit(view=view)
                await interaction.response.defer()

    @app_commands.command(description="Create a new poll")
    @app_commands.guilds(discord.Object(id=utils.guildID))
    @app_commands.check(lambda interaction: checks.check(interaction, "trusted"))
    @app_commands.choices(type=[
        app_commands.Choice(name="Yes/No", value=0)
    ])
    async def poll(self, interaction: discord.Interaction, type: app_commands.Choice[int], channel: app_commands.AppCommandChannel = None):
        if channel != None and channel.type != discord.ChannelType.text:
            await interaction.response.send("Please select a valid text channel!", ephemeral=True)
            return
        if type.value == 0:
            modal = self.modals.YNInitiate()
            modal.supply_params(self, interaction.channel if channel is None else await channel.fetch())
            # modal.supply_params(hide_responders)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"{type}", ephemeral=True)
    
    @poll.error
    async def poll_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("You do not have permission to make a poll!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Polls(bot))