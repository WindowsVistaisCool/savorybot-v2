from discord import Embed, Color
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
        e.add_field(name="Response", value="Your application will be handled by staff members. They have the choice to accept/reject you based on your skill average, networth, slayers, and more. If you get rejected, you cannot apply again. If you feel this is a mistake, you can always DM a staff member.", inline=False)
        return e