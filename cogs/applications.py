import discord
import requests
import json
from discord import ui, app_commands
from discord.ext import commands
from cogs import utils
from typing import Union

def binMod(data: dict = None, *, binID = "62d05c065ecb581b56bc24fa") -> Union[dict, str]:
    header = {
        'Content-Type': 'application/json',
        'X-Master-Key': "$2b$10$xuWXT4f19qj6Gzdnqxn2fuM6XNUB3DpooTJST.YoTfgD35g1mjjQe"
    }
    readHeader = {
        'X-Master-Key': "$2b$10$xuWXT4f19qj6Gzdnqxn2fuM6XNUB3DpooTJST.YoTfgD35g1mjjQe"
    }
    if data is None: return requests.get(f"https://api.jsonbin.io/v3/b/{binID}/latest", json=None, headers=readHeader).json()['record']
    return requests.put(f"https://api.jsonbin.io/v3/b/{binID}", headers=header, json=data).text

# TODO: implement this function so extraneous usernames can be verified
# def toUUID(name):
#     d = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}")
#     if d.status_code == 204:
#         return False
#     return d.json()["id"]

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class views:
        class Application(ui.View):
            def __init__(self, cog):
                self.cog = cog
                super().__init__(timeout=None)

            @ui.button(label="Accept", style=discord.ButtonStyle.success, custom_id="bot::accept")
            async def b_accept(self, interaction: discord.Interaction, butotn: discord.ui.Button) -> None:
                if interaction.user.id not in utils.config['staffMembers']:
                    for role in utils.config['staffRoles']:
                        if role in [r.id for r in interaction.user.roles]:
                            break
                    else:
                        await interaction.response.send_message(f"You do not have permission to accept applications! {debug.debugText()}")
                        return

                binData = binMod()
                del binData['pendingApps'][str(interaction.message.embeds[0].footer.text)]
                binData['acceptedApps'][str(interaction.message.embeds[0].footer.text)] = str(interaction.message.created_at)
                binMod(binData)
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.green()
                embed.set_field_at(2, name="Status", value="Accepted", inline=False)
                await interaction.message.edit(embed=embed, view=None)
                role = interaction.guild.get_role(utils.config['snowflakes']['guildMemberRole'])
                pendingRole = interaction.guild.get_role(utils.config['snowflakes']['pendingRole'])
                member = await interaction.guild.fetch_member(interaction.message.embeds[0].footer.text)
                await member.add_roles(role)
                await member.remove_roles(pendingRole)
                try:
                    await member.send("You have been accepted into `Red Gladiators`!")
                    await interaction.response.defer()
                except:
                    await interaction.response.send_message(f"Failed to send a message to {member.mention}!")

            @ui.button(label="Deny", style=discord.ButtonStyle.danger, custom_id="bot::deny")
            async def b_deny(self, interaction: discord.Interaction, butotn: discord.ui.Button) -> None:
                if interaction.user.id not in utils.config['staffMembers']:
                    for role in utils.config['staffRoles']:
                        if role in [r.id for r in interaction.user.roles]:
                            break
                    else:
                        await interaction.response.send_message(f"You do not have permission to deny applications! {debug.debugText()}")
                        return

                binData = binMod()
                del binData['pendingApps'][str(interaction.message.embeds[0].footer.text)]
                binData['deniedApps'][str(interaction.message.embeds[0].footer.text)] = str(interaction.message.created_at)
                binMod(binData)
                embed = interaction.message.embeds[0]
                embed.color = discord.Color.red()
                embed.set_field_at(2, name="Status", value="Denied", inline=False)
                await interaction.message.edit(embed=embed, view=None)
                role = interaction.guild.get_role(utils.config['snowflakes']['pendingRole'])
                member = await interaction.guild.fetch_member(interaction.message.embeds[0].footer.text)
                await member.remove_roles(role)
                try:
                    await member.send("Sorry, but your application to `Red Gladiators` was denied. You may not apply again unless you talk to a staff member.")
                    await interaction.response.defer()
                except:
                    await interaction.response.send_message(f"Failed to send a message to {member.mention}!")

    class modals:
        class Apply(ui.Modal, title="Apply to Red Gladiators"):
            m_ign = ui.TextInput(label="Minecraft IGN", style=discord.TextStyle.short, min_length=3, max_length=16)

            def supply_cog(self, cog): self.cog = cog

            async def on_submit(self, interaction: discord.Interaction) -> None:
                channel = await interaction.guild.fetch_channel(utils.config["snowflakes"]["appHandlingChannel"])
                binData = binMod()
                failed = False
                if str(interaction.user.id) in binData["pendingApps"].keys():
                    failed = True
                    await interaction.response.send_message(f"You have already submitted an application, the application may have been denied or unanswered. Ask a mod for more help. (Submitted at `{binData['pendingApps'][str(interaction.user.id)]}`)", ephemeral=True)
                if str(interaction.user.id) in binData["acceptedApps"].keys():
                    failed = True
                    await interaction.response.send_message(f"Your application has already been accepted, you may not apply again!", ephemeral=True)
                if str(interaction.user.id) in binData["deniedApps"].keys():
                    failed = True
                    await interaction.response.send_message(f"Sorry, your application has already been denied. Talk to a staff member if you would like to re-apply.", ephemeral=True)
                if failed: return
                binData["pendingApps"][str(interaction.user.id)] = str(interaction.message.created_at)
                binMod(binData)
                embed = discord.Embed(description="New application", color=discord.Color.dark_blue())
                embed.set_footer(text=f"{interaction.user.id}")
                embed.add_field(name="IGN", value=f"`{interaction.data['components'][0]['components'][0]['value']}`", inline=False)
                embed.add_field(name="User", value=f"<@{interaction.user.id}>", inline=False)
                embed.add_field(name="Status", value="Pending", inline=False)
                view = self.cog.views.Application(self.cog)
                await channel.send(embed=embed, view=view)
                role = interaction.guild.get_role(utils.config['snowflakes']['pendingRole'])
                await interaction.user.add_roles(role)
                await interaction.response.send_message("Your application has been sent to the guild admins.", ephemeral=True)
    
    @commands.group()
    @commands.is_owner()
    async def app(self, ctx):
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand.")
    
    @app.command(name="list")
    async def a_list(self, ctx):
        binData = binMod()
        embed = discord.Embed(title="Applications", color=discord.Color.dark_blue())
        for key in binData["pendingApps"].keys():
            embed.add_field(name=f"<@{key}>", value=f"Submitted at `{binData['pendingApps'][key]}`", inline=False)
        await ctx.send(embed=embed)
    
    @app.command(name="raw")
    async def a_raw(self, ctx):
        await ctx.send(f"{binMod()}")

    @app.command(name="del")
    async def a_del(self, ctx, id):
        binData = binMod()
        if id in binData["pendingApps"].keys():
            del binData["pendingApps"][id]
            binMod(binData)
            await ctx.send("Application deleted.")
            return
        if id in binData["acceptedApps"].keys():
            del binData["acceptedApps"][id]
            binMod(binData)
            await ctx.send("Application deleted.")
            return
        if id in binData["deniedApps"].keys():
            del binData["deniedApps"][id]
            binMod(binData)
            await ctx.send("Application deleted.")
            return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Applications(bot))