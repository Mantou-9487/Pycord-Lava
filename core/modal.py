import json
import uuid

from discord.ui import Modal, InputText
from discord import InputTextStyle, Interaction
from lavalink import LoadResult, LoadType, PlaylistInfo, AudioTrack
from typing import Optional

from core.bot import Bot
from core.embeds import LoadingEmbed, SuccessEmbed, ErrorEmbed

class PlaylistModal(Modal):
    def __init__(self, name:str, bot:Bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = bot
        self.name = name

        self.tracks = []

        self.add_item(InputText(label="歌曲連結 (格式為第一首後按下Enter再貼連結，最多25個)", placeholder="請將連結貼至輸入框中", style=InputTextStyle.paragraph))

    async def callback(self, interaction: Interaction) -> Optional[LoadResult]:
        with open(f"./playlist/{interaction.user.id}.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        if not len(self.children[0].value.split("\n")) > 25 and not (len(data[self.name]['tracks']) + len(self.children[0].value.split("\n"))) > 25:
            await interaction.response.send_message(embed=LoadingEmbed(title="正在讀取中..."))
            
            for query in self.children[0].value.split("\n"):
                result = await self.bot.lavalink.get_tracks(query)
                for track in result.tracks:
                    data[self.name]['tracks'].append({
                        'track': track.track,       
                        'identifier': track.identifier,
                        'isSeekable': track.is_seekable,
                        'author': track.author,
                        'length': track.duration,
                        'isStream': track.stream,
                        'title': track.title,
                        'uri': f"https://www.youtube.com/watch?v={track.identifier}"
                    })
                            
            for name in data.keys():
                if uuid.uuid5(uuid.NAMESPACE_DNS, name).hex == self.name:
                    self.name = name
                    break

            data[self.name]["tracks"] = data[self.name]['tracks']

            with open(f"./playlist/{interaction.user.id}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            
            await interaction.edit_original_response(embed=SuccessEmbed(title="添加成功!"))
        else:
            await interaction.edit_original_response(embed=ErrorEmbed(title="你給的連結太多了或是歌單超出限制了! (最多25個)",description=f"目前歌單中的歌曲數量: {len(data[self.name]['tracks'])}"))