# AT PROJECT Limited 2022 - 2024; AT_nEXT-v3.6-beta.2
import asyncio

from discord import ui
from discord import Embed
from discord import Interaction
from discord import ButtonStyle

from player import Track

class ListView(ui.View):
    def __init__(self, lst: list | Track, list_length: int, pages: int,
                 page: int, is_queue: bool = False, position: int = None):
        super().__init__()
        self.length = list_length
        self.position = position
        self.page = page
        self.pages = pages
        self.time = 0
        self.is_queue = is_queue
        self.lst: list[Track | str] = lst

    async def time_stop(self):
        while True:
            await asyncio.sleep(1)
            self.time += 1
            
            if self.time > 10:
                self.stop()
                return

    async def __print_list(self, interaction: Interaction):
        retval = ""
        embed = Embed(color=0x915AF2)

        if self.page == 1:
            srt, stp = 0, 9
        else:
            srt = 10 * (self.page - 1) - 1
            stp = 10 * self.page - 1
    
        for i in range(srt, stp):
            if i > self.length - 1:
                break

            if type(self.lst[i]) == Track:
                title = self.lst[i].get_track().title
            else:
                title = self.lst[i][0]

            if len(title) > 65:
                title = title[:-(len(title) - 65)] + "..."

            if self.is_queue and i == self.player.position:
                retval += f"**{i + 1}. " + title + "\n**"
                continue

            retval += f"{i + 1}. " + title + "\n"
        
        embed.add_field(name="📄 User list", value=retval)
        embed.set_footer(text=f"Page: {self.page} of {self.pages}\n")
        
        await interaction.response.edit_message(embed=embed)

    @ui.button(label="⬅️ Previous", style=ButtonStyle.primary)
    async def prev_button(self, interaction: Interaction, button: ui.Button) -> None:
        if self.page != 1:
            self.page -= 1
            self.time = 0
            
            await self.__print_list(interaction)
            return
        
        if self.pages == 1:
            await interaction.response.defer()
            return

        self.page = self.pages
        self.time = 0
        await self.__print_list(interaction)

    @ui.button(label="Next ➡️", style=ButtonStyle.primary)
    async def next_button(self, interaction: Interaction, button: ui.Button) -> None:
        if self.page != self.pages:
            self.page += 1
            self.time = 0

            await self.__print_list(interaction)
            return

        if self.pages == 1:
            await interaction.response.defer()
            return

        self.page = 1
        self.time = 0
        await self.__print_list(interaction)