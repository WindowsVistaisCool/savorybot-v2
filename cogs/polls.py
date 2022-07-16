import discord
from discord import ui, app_commands
from discord.ext import commands
from cogs import utils, checks
from typing import Literal
from datetime import datetime
from random import choice

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
                if interaction.user.mention in embed.fields[2].value:
                    await interaction.response.send_message("You cannot up/down vote again!", ephemeral=True)
                    return
                if interaction.data['custom_id'].startswith("bot::poll::0::vu"):
                    embed.set_field_at(0, name="Yes", value=f"***{int(embed.fields[0].value[3:-3]) + 1}***")
                else:
                    embed.set_field_at(1, name="No", value=f"***{int(embed.fields[1].value[3:-3]) + 1}***")
                embed.set_field_at(2, name="Participants", value=(embed.fields[2].value if embed.fields[2].value != 'None' else "") + f"{interaction.user.mention}", inline=False)
                await message.edit(embed=embed)
        elif interaction.data['custom_id'].startswith("bot::poll::1"):
            embed = message.embeds[0]
            if interaction.user.mention in embed.fields[-1].value:
                await interaction.response.send_message("You cannot vote again!", ephemeral=True)
                return
            values = interaction.data['values'][0].split('-')
            embed.set_field_at(int(values[0]), name=values[1], value=f"***{int(embed.fields[int(values[0])].value[3:-3]) + 1}***")
            embed.set_field_at(-1, name="Participants", value=(embed.fields[-1].value if embed.fields[-1].value != 'None' else "") + f" {interaction.user.mention}", inline=False)
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
        
        class SelectPoll(ui.View):
            def __init__(self, cog, pollID, pollChannel, options):
                self.cog = cog
                self.pollID = pollID
                self.pollChannel = pollChannel
                super().__init__(timeout=None)
                self.add_item(self.s_select(pollID, pollChannel, options))
            
            class s_select(ui.Select):
                def __init__(self, pollID, pollChannel, options: list):
                    super().__init__(
                        row=0,
                        placeholder="Select an option",
                        custom_id=f"bot::poll::1-{pollID}-{pollChannel}",
                        options=[discord.SelectOption(emoji=choice(list("🍏🍎🍐🍊🍋🍌🍉🍇🍓🍈🍒🍑🥭🍍🥥🥝🍅🍆🥑")), label=i, value=f"{options.index(i)}-{i}") for i in options]
                    )
                
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
        
        class SelectInitiate(ui.Modal, title="Start a Select poll"):
            m_title = ui.TextInput(label="Poll Title", style=discord.TextStyle.paragraph, max_length=256)
            m_opt1 = ui.TextInput(label="Option 1 (Required)", style=discord.TextStyle.short, max_length=100)
            m_opt2 = ui.TextInput(label="Option 2 (Required)", style=discord.TextStyle.short, max_length=100)
            m_opt3 = ui.TextInput(label="Option 3", style=discord.TextStyle.short, max_length=100, required=False)
            m_opt4 = ui.TextInput(label="Option 4", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt5 = ui.TextInput(label="Option 5", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt6 = ui.TextInput(label="Option 6", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt7 = ui.TextInput(label="Option 7", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt8 = ui.TextInput(label="Option 8", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt9 = ui.TextInput(label="Option 9", style=discord.TextStyle.short, max_length=100, required=False)
            # m_opt10 = ui.TextInput(label="Option 10", style=discord.TextStyle.short, max_length=100, required=False)

            def supply_params(self, cog, channel) -> None:
                self.cog = cog
                self.channel = channel
            
            async def on_submit(self, interaction: discord.Interaction):
                embed = discord.Embed(title=interaction.data['components'][0]['components'][0]['value'], color=discord.Color.blurple(), timestamp=datetime.now())
                embed.set_footer(text="Started at")
                existingOptions = []
                for i in interaction.data['components'][1:]:
                    if i['components'][0]['value'] == "": continue
                    if i['components'][0]['value'] in existingOptions:
                        await interaction.response.send_message("You can't have duplicate options!", ephemeral=True)
                        return
                    embed.add_field(name=i['components'][0]['value'], value="***0***")
                    existingOptions.append(i['components'][0]['value'])
                embed.add_field(name="Participants", value="None", inline=False)
                message = await self.channel.send(embed=embed)
                options = []
                for i in interaction.data['components'][1:]:
                    if i['components'][0]['value'] != "": options.append(i['components'][0]['value'])
                view = self.cog.views.SelectPoll(self.cog, message.id, self.channel.id, options)
                await message.edit(view=view)
                await interaction.response.defer()

    @app_commands.command(description="Create a new poll")
    @app_commands.guilds(discord.Object(id=utils.guildID))
    @app_commands.check(lambda interaction: checks.check(interaction, "trusted"))
    @app_commands.choices(type=[
        app_commands.Choice(name="Yes/No", value=0),
        app_commands.Choice(name="Select", value=1)
    ])
    async def poll(self, interaction: discord.Interaction, type: app_commands.Choice[int], channel: app_commands.AppCommandChannel = None):
        if channel != None and channel.type != discord.ChannelType.text:
            await interaction.response.send("Please select a valid text channel!", ephemeral=True)
            return
        if type.value == 0:
            modal = self.modals.YNInitiate()
            modal.supply_params(self, interaction.channel if channel is None else await channel.fetch())
            await interaction.response.send_modal(modal)
        elif type.value == 1:
            modal = self.modals.SelectInitiate()
            modal.supply_params(self, interaction.channel if channel is None else await channel.fetch())
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Unknown poll type: {type}", ephemeral=True)
    
    @poll.error
    async def poll_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message("You do not have permission to make a poll!", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Polls(bot))