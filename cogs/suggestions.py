import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime
from cogs import utils, embeds, checks

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def event_callback(cls, interaction: discord.Interaction) -> None:
        suggestID = int(interaction.data["custom_id"].split("-")[1])
        channel = interaction.guild.get_channel(utils.config['snowflakes']["suggestionsChannel"])
        message = await channel.fetch_message(suggestID)
        if interaction.data['custom_id'].startswith("bot::sgst::v"):
            embed = message.embeds[0]
            if interaction.user.mention in embed.fields[1].value:
                await interaction.response.send_message("You cannot up/down vote again!", ephemeral=True)
                return
            embed.set_field_at(0, name="Score", value=f"`{int(embed.fields[0].value[1:-1]) + (1 if interaction.data['custom_id'].startswith('bot::sgst::vu') else -1)}`", inline=False)
            embed.set_field_at(1, name="Respondants", value=(embed.fields[1].value if embed.fields[1].value != 'None' else "") + f"{interaction.user.mention}", inline=False)
            await message.edit(embed=embed)
        elif interaction.data['custom_id'].startswith("bot::sgst::mod-"):
            if not await checks.check(interaction, "staff"):
                await interaction.response.send_message("You do not have permission to perform this action!", ephemeral=True)
                return
            await message.edit(view=cls.views.ModSettingsActive(suggestID, cls.views.Pending, channel, interaction.guild, interaction.user.id))
        await interaction.response.defer()
    
    class views:
        class Pending(ui.View):
            def __init__(self, suggestID):
                self.suggestID = suggestID
                super().__init__(timeout=None)
                self.add_item(self.b_upvote(self.suggestID))
                self.add_item(self.b_downvote(self.suggestID))
                self.add_item(self.b_modSettings(self.suggestID))

            class b_modSettings(ui.Button):
                def __init__(self, suggestID):
                    super().__init__(label="Settings", style=discord.ButtonStyle.secondary, custom_id=f"bot::sgst::mod-{suggestID}")
                async def callback(self, interaction: discord.Interaction): pass
            
            class b_upvote(ui.Button):
                def __init__(self, suggestID):
                    super().__init__(emoji="👆", style=discord.ButtonStyle.primary, custom_id=f"bot::sgst::vu-{suggestID}")
                async def callback(self, interaction: discord.Interaction): pass
            
            class b_downvote(ui.Button):
                def __init__(self, suggestID):
                    super().__init__(emoji="👇", style=discord.ButtonStyle.primary, custom_id=f"bot::sgst::vd-{suggestID}")
                async def callback(self, interaction: discord.Interaction): pass
        
        class ModSettingsActive(ui.View):
            def __init__(self, suggestID, pendingView, messageChannel, messageGuild, ownerID):
                self.suggestID = suggestID
                self.pendingView = pendingView
                self.channel = messageChannel
                self.guild = messageGuild
                self.ownerID = ownerID
                super().__init__(timeout=20.0)
                self.add_item(self.pendingView.b_upvote(self.suggestID))
                self.add_item(self.pendingView.b_downvote(self.suggestID))
                self.add_item(self.b_exit())
                self.add_item(self.b_accept())
                self.add_item(self.b_reject())
                self.sentBack = False
            
            async def back(self):
                message = await self.channel.fetch_message(self.suggestID)
                self.sentBack = True
                await message.edit(view=self.pendingView(self.suggestID))

            async def checkPerms(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id == self.ownerID:
                    return True
                else:
                    await interaction.response.send_message("You do not have permission to perform this action!", ephemeral=True)
                    return False
            
            class b_exit(ui.Button):
                def __init__(self):
                    super().__init__(label="Exit Settings", style=discord.ButtonStyle.secondary)
                async def callback(self, interaction: discord.Interaction):
                    if not await self.view.checkPerms(interaction): return
                    await interaction.response.defer()
                    await self.view.back()

            class b_accept(ui.Button):
                def __init__(self):
                    super().__init__(label="Accept", style=discord.ButtonStyle.success)
                async def callback(self, interaction: discord.Interaction):
                    if not await self.view.checkPerms(interaction): return
                    await interaction.response.defer()
                    message = await self.view.channel.fetch_message(self.view.suggestID)
                    embed = message.embeds[0]
                    embed.color = discord.Color.green()
                    embed.set_field_at(2, name="Status", value="Accepted", inline=False)
                    try:
                        member = await self.view.guild.fetch_member(int(embed.fields[3].value[1:-1]))
                        await member.send(f"Your suggestion has been accepted! Your suggestion reached a score of {embed.fields[0].value}.")
                    except: pass
                    self.sentBack = True
                    await message.edit(embed=embed, view=None)
            
            class b_reject(ui.Button):
                def __init__(self):
                    super().__init__(label="Reject", style=discord.ButtonStyle.danger)
                async def callback(self, interaction: discord.Interaction):
                    if not await self.view.checkPerms(interaction): return
                    await interaction.response.defer()
                    message = await self.view.channel.fetch_message(self.view.suggestID)
                    embed = message.embeds[0]
                    embed.color = discord.Color.red()
                    embed.set_field_at(2, name="Status", value="Rejected", inline=False)
                    try:
                        member = await self.view.guild.fetch_member(int(embed.fields[3].value[1:-1]))
                        await member.send(f"Your suggestion has been rejected. Your suggestion reached a score of {embed.fields[0].value}.")
                    except: pass
                    self.sentBack = True
                    await message.edit(embed=embed, view=None)

            async def on_timeout(self):
                if not self.sentBack: await self.back()

    class modals:
        class Initiate(ui.Modal, title="Make a suggestion"):
            m_suggestion = ui.TextInput(label="Suggestion", style=discord.TextStyle.paragraph, max_length=1000)

            def supply_cog(self, cog): self.cog = cog

            async def on_submit(self, interaction: discord.Interaction):
                channel = interaction.guild.get_channel(utils.config['snowflakes']['suggestionsChannel'])
                embed = discord.Embed(title="New suggestion", description=interaction.data['components'][0]['components'][0]['value'], color=discord.Color.blurple(), timestamp=datetime.now())
                embed.set_footer(text="Suggested at")
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                embed.add_field(name="Score", value="`0`", inline=False)
                embed.add_field(name="Respondants", value="None", inline=False)
                embed.add_field(name="Status", value="Pending", inline=False)
                embed.add_field(name="Author ID", value=f"`{interaction.user.id}`")
                message = await channel.send(embed=embed)
                await message.edit(view=self.cog.views.Pending(message.id))
                await interaction.response.send_message("Thank you for your suggestion, it has been sent to the suggestions channel.", ephemeral=True)

    @app_commands.command(description="Make a suggestion")
    @app_commands.guilds(discord.Object(id=utils.guildID))
    async def suggest(self, interaction: discord.Interaction):
        modal = self.modals.Initiate()
        modal.supply_cog(self)
        await interaction.response.send_modal(modal)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Suggestions(bot))