# AT PROJECT Limited 2022 - 2023; ATLB_nEXT-1.7.13.1_dev2.0-0.2
import math
import asyncio

from discord import ui
from discord import Embed
from discord import Interaction
from discord import ButtonStyle

class ListControl(ui.View):
    def __init__(self, queue: list, song_title: str):
        super().__init__()

        self.page = 1
        self.pages = math.ceil(len(queue) / 10 + 0.1)
        self.time = 0 

        self.music_queue = queue
        self.song_title = song_title


    async def time_stop(self):
        while True:
            await asyncio.sleep(1)
            self.time += 1
            
            if self.time > 10:
                self.stop()
                return


    async def __print_list(self, interaction: Interaction, button: ui.Button):
        retval = ""
        embed = Embed(color=0x915AF2)
        pages = math.ceil(len(self.music_queue) / 10 + 0.1)

        if self.page == 1:
            srt, stp = 0, 10
        else:
            srt = 10 * (self.page - 1)
            stp = 10 * self.page

        for i in range(srt, stp):
            if i > len(self.music_queue) - 1:
                break
            if len(self.music_queue[i][0].title) > 65:
                z = len(self.music_queue[i][0].title) - 65
                title = self.music_queue[i][0].title[:-z] + "..."
            else:
                title = self.music_queue[i][0].title

            if self.song_title == self.music_queue[i][0].title:
                retval += "**  • " + title + "**\n"
                continue

            retval += f"{i + 1}. " + title + "\n"
            
        embed.add_field(name="📄 Playlist", value=retval)
        embed.set_footer(text=f"Page: {self.page} of {pages}\n")
        
        await interaction.response.edit_message(embed=embed)


    @ui.button(label="Previous", style=ButtonStyle.primary)
    async def prev_button(self, interaction: Interaction, button: ui.Button) -> None:
        if self.page != 1:
            self.page -= 1
            self.time = 0
            
            await self.__print_list(interaction, button)


    @ui.button(label="Next", style=ButtonStyle.primary)
    async def next_button(self, interaction: Interaction, button: ui.Button) -> None:
        if self.page != self.pages:
            self.page += 1
            self.time = 0

            await self.__print_list(interaction, button)
