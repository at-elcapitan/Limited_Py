from discord.ext import commands
from logger import logger

class Bot(commands.Bot):
    def __init__(self, commands_prefix, intents):
        super().__init__(command_prefix=commands_prefix, intents=intents)

    async def async_cleanup(self):
        await self.cogs['music_cog'].bot_cleanup()
    
    async def close(self):
        logger.info("Cleaning up...")
        await self.async_cleanup()
        logger.info("Shutting down")
        await super().close()