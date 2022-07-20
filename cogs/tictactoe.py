import discord
from discord import app_commands, ui
from discord.ext import commands
from cogs import utils
from enum import Enum
from datetime import datetime

class Tictactoe(commands.Cog):
    guid = utils.guildID
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def event_callback(cls, interaction: discord.Interaction):
        gameID, owner, opponent = interaction.data['custom_id'].split('-')[1:4]
        message = await interaction.channel.fetch_message(int(gameID))
        if interaction.data['custom_id'].startswith("bot::tictactoe::a") or interaction.data['custom_id'].startswith("bot::tictactoe::d"):
            if interaction.user.id != int(opponent):
                await interaction.response.send_message("You cannot accept/decline this!", ephemeral=True)
                return
            if interaction.data['custom_id'].startswith("bot::tictactoe::a"):
                view = cls.views.structs.Game(gameID, None, opponent, owner, None)
                await message.edit(content=f"Challenge accepted by <@!{opponent}>! It is now <@!{opponent}>'s turn. Click any open (⚔️) space to begin.", embed=None, view=view)
            else:
                embed = message.embeds[0]
                embed.color = discord.Color.brand_red()
                embed.description = f"Challenge declined by <@!{opponent}>!"
                embed.timestamp = datetime.now()
                embed.set_footer(text=f"Challenge was declined at")
                await message.edit(content=None, embed=embed, view=None)
        elif interaction.data['custom_id'].startswith("bot::tictactoe::g_"):
            if interaction.user.id != int(owner):
                await interaction.response.send_message("It isn't your turn!", ephemeral=True)
                return
            gameData = interaction.data['custom_id'].split('::')[2].split('-')[0].split('_')
            gameBoard = []
            conv = {
                discord.ButtonStyle.primary: 0,
                discord.ButtonStyle.success: 1,
                discord.ButtonStyle.secondary: 2
            }
            conv2 = ["❌", "⭕"]
            for component in interaction.message.components:
                if not isinstance(component, discord.ActionRow): continue
                row = []
                for i in component.children:
                    if not isinstance(i, discord.Button): continue
                    row.append(conv[i.style])
                gameBoard.append(row)
            
            # Update board and swap button IDs
            gameBoard[int(gameData[2])][int(gameData[3])] = int(gameData[1])
            updatedMessage = await interaction.message.edit(content=f"It is now <@!{opponent}>'s ({conv2[int(gameData[1]) ^ 1]}) turn.", view=cls.views.structs.Game(gameID, gameBoard, int(opponent), int(owner), int(gameData[1]) ^ 1))

            # Check for winner? (2 = None/Tie)
            winStatus = 2
            for row in range(3):
                if gameBoard[row][0] != 2 and gameBoard[row][0] == gameBoard[row][1] and gameBoard[row][0] == gameBoard[row][2]:
                    winStatus = gameBoard[row][0]
                    break
            for col in range(3):
                if gameBoard[0][col] != 2 and gameBoard[0][col] == gameBoard[1][col] and gameBoard[0][col] == gameBoard[2][col]:
                    winStatus = gameBoard[0][col]
                    break
            # Diagonals
            if gameBoard[0][0] != 2 and gameBoard[0][0] == gameBoard[1][1] and gameBoard[0][0] == gameBoard[2][2]: winStatus = gameBoard[0][0]
            if gameBoard[2][0] != 2 and gameBoard[2][0] == gameBoard[1][1] and gameBoard[2][0] == gameBoard[0][2]: winStatus = gameBoard[2][0]
            
            # Check for tie or win
            if winStatus != 2:
                player = await interaction.guild.fetch_member(int(owner))
                await message.edit(content=f"{player.mention} ({conv2[int(gameData[1]) ^ 1]}) won!", view=cls.views.structs.EndedGame(items=updatedMessage.components))

                await interaction.response.send_message("You won! Congrats!", ephemeral=True)
                return
            else:
                toBreak = False
                for row in gameBoard:
                    for item in row: 
                        if item == 2: toBreak = True
                    if toBreak: break
                else:
                    player = await interaction.guild.fetch_member(int(owner))
                    await message.edit(content=f"The game tied!", view=cls.views.structs.EndedGame(items=updatedMessage.components))
                    await interaction.response.send_message("It's a draw!", ephemeral=True)
                    return
        await interaction.response.defer()
    
    class views:
        class structs:
            class Prompt(ui.View):
                def __init__(self, messageID, owner, opponent):
                    super().__init__(timeout=None)
                    self.add_item(self.b_accept(messageID, owner, opponent))
                    self.add_item(self.b_decline(messageID, owner, opponent))
                
                class b_accept(ui.Button):
                    def __init__(self, messageID, owner, opponent): super().__init__(style=discord.ButtonStyle.success, emoji="✅", custom_id=f"bot::tictactoe::a-{messageID}-{owner}-{opponent}")
                    async def callback(self, interaction: discord.Interaction): pass
                
                class b_decline(ui.Button):
                    def __init__(self, messageID, owner, opponent): super().__init__(style=discord.ButtonStyle.danger, emoji="✖️", custom_id=f"bot::tictactoe::d-{messageID}-{owner}-{opponent}")
                    async def callback(self, interaction: discord.Interaction): pass

            class Game(ui.View):
                def __init__(self, gameID, states: list, owner: int, opponent: int, piece: int):
                    super().__init__(timeout=None)
                    if states == None: states = [[2, 2, 2], [2, 2, 2], [2, 2, 2]]
                    if piece == None: piece = 0
                    for i in range(3):
                        for x in range(3):
                            self.add_item(self.b_generic(
                                (
                                    lambda emoji: ["❌", "⭕", "⚔️"][emoji],
                                    lambda color: [discord.ButtonStyle.primary, discord.ButtonStyle.success, discord.ButtonStyle.secondary][color]
                                ),
                                i,
                                x,
                                gameID,
                                states[i][x],
                                owner,
                                opponent,
                                piece
                            ))

                class b_generic(ui.Button):
                    def __init__(self, callables, row, col, gameID, state, owner, opponent, piece): super().__init__(emoji=callables[0](state), row=row, style=callables[1](state), custom_id=f"bot::tictactoe::g_{piece}_{row}_{col}-{gameID}-{owner}-{opponent}", disabled=state != 2)
                    async def callback(self, interaction: discord.Interaction): pass
            
            class EndedGame(ui.View):
                def __init__(self, items):
                    super().__init__(timeout=None)
                    row = 0
                    for actionRow in items:
                        for i in actionRow.children: self.add_item(self.b_generic(i, row))
                        row += 1
                    
                class b_generic(ui.Button):
                    def __init__(self, button, row): super().__init__(emoji=button.emoji, style=button.style, row=row, disabled=True)
                    async def callback(self, interaction: discord.Interaction): pass
    
        class actives:
            pass

    class modals:
        pass

    @app_commands.command(name="tictactoe", description="Play a game of Tic-Tac-Toe with another user.")
    @app_commands.guilds(discord.Object(id=guid))
    async def s_tictactoe(self, interaction: discord.Interaction, user: discord.User):
        if user.bot:
            await interaction.response.send_message("You can't play with bots!", ephemeral=True)
            return
        if user.id == interaction.user.id:
            await interaction.response.send_message("You can't play with yourself!", ephemeral=True)
            return
        embed = discord.Embed(title="Tic Tac Toe", color=discord.Color.blurple(), timestamp=datetime.now(), description=f"{interaction.user.mention} has challenged {user.mention} to a game of Tic Tac Toe!")
        embed.set_footer(text="Click the ✅ button to accept, or the ✖️ button to decline. | Request sent at")
        embed.set_author(name="requested by " + interaction.user.name, icon_url=interaction.user.avatar.url)
        message = await interaction.channel.send(f"{user.mention}, someone has challenged you!", embed=embed)
        view = self.views.structs.Prompt(message.id, interaction.user.id, user.id)
        await message.edit(view=view)
        await interaction.response.send_message("Your challenge has been sent!", ephemeral=True)

    @commands.command()
    @commands.is_owner()
    async def tictactoe(self, ctx, user: discord.User = None):
        await ctx.message.delete()
        gen = lambda: [2 for _ in range(3)]
        items = [gen() for _ in range(3)]
        if user == None: user = ctx.author
        message = await ctx.send(f"Game ({ctx.author.mention} vs {user.mention})")
        view = self.views.structs.Game(gameID=message.id, states=items, owner=ctx.author.id, opponent=user.id, piece=0)
        await message.edit(view=view)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tictactoe(bot))