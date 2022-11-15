import discord
from discord.ext import commands
from embeds import errorEmbedCustom, eventEmbed

class kernel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
