# AT PROJECT Limited 2022 - 2024; ATLB-v3.2-gpl3
import asyncio

from discord import ui
from discord import Embed
from discord import Interaction
from discord import ButtonStyle

class ListView(ui.View):
    def __init__(self, ulist: list, pages: int, position: int, is_queue: bool = False, 
                 current_position: int = None):
        super().__init__()

        self.page = position
        self.pages = pages
        self.time = 0
        self.is_queue = is_queue 
        self.song_position = current_position

        self.ulist = ulist


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
            if i > len(self.ulist) - 1:
                break
            
            title = self.ulist[i][0] if not self.is_queue else self.ulist[i][0].title

            if len(title) > 65:
                title = title[:-(len(title) - 65)] + "..."

            if self.is_queue and i == self.song_position:
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
