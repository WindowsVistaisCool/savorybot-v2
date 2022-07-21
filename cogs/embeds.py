from discord import Embed, Color
from datetime import datetime
from typing import Optional

class EmbedParser:
    def parse(self, data: dict) -> Optional[Embed]:
        """
        check all data entries corresponding to elements on the embed
        if they are not present, do not include them in the embed
        if required elements are not included, return None
        """
        if 'title' not in data.keys() and 'description' not in data.keys():
            return None
        embed = Embed(
            title=data['title'] if 'title' in data.keys() else "",
            description=data['description'] if 'description' in data.keys() else "",
            color=data['color'] if 'color' in data.keys() else None,
            url=data['url'] if 'url' in data.keys() else None,
            timestamp=data['timestamp'] if 'timestamp' in data.keys() else None
        )
        if 'thumbnail' in data.keys(): embed.set_thumbnail(url=data['thumbnail'])
        if 'image' in data.keys(): embed.set_image(url=data['image'])
        if 'footer' in data.keys(): embed.set_footer(text=data['footer'][0], icon_url=data['footer'][1] if len(data['footer']) > 1 else None)
        if 'author' in data.keys(): embed.set_author(name=data['author'][0], url=data['author'][1] if len(data['footer']) > 1 else None, icon_url=data['author'][2] if len(data['author']) > 2 else None)
        for field in data['fields']:
            embed.add_field(name=field[0], value=field[1], inline=bool(field[2]) if len(field) > 1 else False)
        return embed

class presets:
    @staticmethod
    def apply() -> Embed:
        e = Embed(title="Guild Applications", color=Color.blurple())
        e.add_field(name="How to apply", value="Click the green 'Apply' button and enter your Minecraft IGN into the text field.", inline=False)
        e.add_field(name="API", value="If you do not have your APIs (skills, collections, enderchest, **and** inventory) on, your application will be instantly rejected.", inline=False)
        e.add_field(name="Response", value="Your application will be handled by staff members. They have the choice to accept/reject you based on your skill average, networth, slayers, and more. **Your application will be based off requirements listed above**. If you are rejected, you cannot apply again. If you feel this is a mistake, you can always DM a staff member.", inline=False)
        return e
    
    @staticmethod
    def verify() -> Embed:
        e = Embed(title="Verify Your Account", color=Color.blurple())
        e.add_field(name="How to verify", value="Make sure you have read the rules, then click the blue 'Verify' button below.", inline=False)
        return e

    @staticmethod
    def giveaways() -> Embed:
        e = Embed(title="Giveaway Guidelines", color=Color.blurple())
        e.add_field(name="Basic Guidelines", value="""_\>_    You may host up to 4 giveaways per week.
_\>_    You may set your item to a split amount (ex. `2mil coins`) that are shared across multiple winners (ex. `1mil` per winner).
_\>_    You may not giveaway more than 10 items per giveaway (ex. 50 `bank 1` books).
_\>_    The item(s) being given away do not have to be skyblock-related (ex. dank memer coins).
_\>_    The total value of item(s) must be greater than `250,000 coins` (skyblock only).
_\>_    They must have real value (ex. `Clay XI minion`, not dirt)""", inline=False)
        e.add_field(name="Hosting Requirements", value="""_\>_    You must be a member of Red Gladiators (applies to all items).
_\>_    You are held responsible for your items. If you lose them before the giveaway time is up and refuse to find replacements, you will be considered scamming and will be kicked from the guild.
_\>_    If (rare cases only) you cannot deliver an item, you may choose to give it to a staff member (or trusted) to give away that item for you, and you will not be held accountable if it goes missing, as long as there is proof.
_\>_    ***YOU MAY NOT ENTER YOUR OWN GIVEAWAY!*** If you do and you win, you will get a warning and will not be allowed to create giveaways for _1 week_.""", inline=False)
        e.add_field(name="Ending Guidelines", value="""_\>_    You must provide image proof that you have given the prize.
_\>_    If you (or the recipient) have not shown proof within 3 days, you will be kicked from the guild for scamming.
_\>_    If you break a rule, punishment is up to staff discretion.
_\>_    You will be given the <@&840038424332337202> role""", inline=False)
        e.add_field(name="Participant Requirements", value="""_\>_    If you are not active on skyblock, please do not enter giveaways (unless noted by the host).""", inline=False)
        return e
    
    @staticmethod
    def giveaway_starting() -> Embed:
        e = Embed(title="Starting a giveaway", color=Color.brand_green())
        e.add_field(name="If you have trusted or higher", value="If you have <@&789592055600250910> or higher, you may start giveaways in the <#804387030812983317> channel by using the command: `!gstart <time> <# of winners> <prize>`. Example: `!gstart 3d 1w T3 Carrot Hoe` will start a giveaway for 3 days with 1 winner receiving a T3 Carrot Hoe.", inline=False)
        e.add_field(name="Normal Members", value="If you do not have <@&789592055600250910> or higher, you can contact a trusted or staff member and they may start your giveaway for you.", inline=False)
        return e

    @staticmethod
    def guide_polls() -> Embed:
        e = Embed(title="Polls Guide", color=Color.brand_green(), timestamp=datetime.now())
        e.set_footer(text="Last updated")
        e.add_field(name="Permission Level", value="<@&789592055600250910>***+***", inline=False)
        e.add_field(name="How to create a poll", value="Type `/poll` in any channel, then select the type of poll. If needed, press `TAB` to get to the optional `channel` parameter where you can select a text channel and the poll will be sent there instead. This however is not required, and defaults to the current channel you are in.", inline=False)
        e.add_field(name="Ending a poll", value="***[Permission***: <@&788912937481273344>***+]***\nTo end a poll, reply to the poll (the one the bot sent) with `=nv`, and it will remove the ability for users to make responses.", inline=False)
        e.add_field(name="Simple Yes/No Polls", value="`/poll type:Yes/No` will create a yes/no poll. A prompt will appear for you to enter the poll title.", inline=False)
        e.add_field(name="Four option custom", value="`/poll type:Select` will create a poll with four options. A prompt will appear for you to enter the poll title and two required options, as well as two other options.", inline=False)
        return e
    
    @staticmethod
    def guide_apps() -> Embed:
        e = Embed(title="Applications Guide", color=Color.brand_red(), timestamp=datetime.now())
        e.set_footer(text="Last updated")
        e.add_field(name="Permission Level", value="<@&792875711676940321>***+***", inline=False)
        e.add_field(name="Handling Applications", value="Any applications that a user sends will create a request in <#831579949415530527>. Two buttons will appear to accept/reject the application. When a button is pressed, the applicant will recieve a DM telling them if they were accepted or not. If they were accepted **OR** rejected, they **will not be able to apply again**.", inline=False)
        e.add_field(name="Deleting Applications", value="***[Permission***: <@&788912937481273344>***+]***\nIf an application needs to be deleted (pending, accepted, or declined already), you can use `=app del <id>` where `<id>` is the application ID found near the bottom of the application.", inline=False)
        return e