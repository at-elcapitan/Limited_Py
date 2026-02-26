# AT PROJECT Limited 2022 - 2024; nEXT-v4.0_beta.1

import asyncio
from discord import ui, Embed, Interaction, ButtonStyle
from player import Track


class ListView(ui.View):
    ITEMS_PER_PAGE = 10
    TIMEOUT_SECONDS = 10

    def __init__(
            self,
            lst: list[Track],
            list_length: int,
            pages: int,
            page: int,
            is_queue: bool = False,
            position: int | None = None
        ):
        super().__init__()

        self.lst = lst
        self.length = list_length
        self.pages = pages
        self.page = page
        self.is_queue = is_queue
        self.position = position

        self._elapsed = 0

    async def time_stop(self):
        while not self.is_finished():
            await asyncio.sleep(1)
            self._elapsed += 1

            if self._elapsed >= self.TIMEOUT_SECONDS:
                self.stop()
                break

    async def _render_page(self, interaction: Interaction):
        embed = Embed(color=0x915AF2)

        start = (self.page - 1) * self.ITEMS_PER_PAGE
        end = start + self.ITEMS_PER_PAGE
        items = self.lst[start:end]

        lines = []

        for index, item in enumerate(items, start=start):
            if isinstance(item, Track):
                title = item.get_track().title
            else:
                title = item[0] if isinstance(item, (list, tuple)) else str(item)

            if len(title) > 65:
                title = title[:65] + "..."

            line = f"{index + 1}. {title}"

            if self.is_queue and self.position is not None and index == self.position:
                line = f"**{line}**"

            lines.append(line)

        embed.add_field(
            name="📄 User list",
            value="\n".join(lines) if lines else "No items to display.",
            inline=False,
        )
        embed.set_footer(text=f"Page: {self.page} of {self.pages}")

        await interaction.response.edit_message(embed=embed, view=self)

    def _reset_timeout(self):
        self._elapsed = 0

    @ui.button(label="⬅️ Previous", style=ButtonStyle.primary)
    async def prev_button(self, interaction: Interaction, _: ui.Button):
        if self.pages <= 1:
            await interaction.response.defer()
            return

        self.page = self.page - 1 if self.page > 1 else self.pages
        self._reset_timeout()
        await self._render_page(interaction)

    @ui.button(label="Next ➡️", style=ButtonStyle.primary)
    async def next_button(self, interaction: Interaction, _: ui.Button):
        if self.pages <= 1:
            await interaction.response.defer()
            return

        self.page = self.page + 1 if self.page < self.pages else 1
        self._reset_timeout()
        await self._render_page(interaction)