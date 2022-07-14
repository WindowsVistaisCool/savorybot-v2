from discord import Embed
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