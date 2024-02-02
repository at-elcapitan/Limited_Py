print("AT PROJECT Limited, 2022 - 2023;  ATLB-v3.4")
print("Product licensed by GPLv3, file `LICENSE`")
print("The license applies to all project files since ATLB-v3.2-gpl3")
import os
import sys
import logging
from datetime import datetime

import discord
from discord.ext import commands

import psycopg2
import wavelink
import colorama
from wavelink.ext import spotify

import embeds
from exceptions import FileError
from music import music_cog

# Logger setup
colorama.init(autoreset=True)
class ColoredFormatter(logging.Formatter):
    COLOR_MAP = {
        'DEBUG': colorama.Fore.BLUE,
        'INFO': colorama.Fore.GREEN,
        'WARN': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRIT': colorama.Fore.MAGENTA,
    }

    def format(self, record):
        if record.levelname == 'WARNING':
            record.levelname = 'WARN'

        if record.levelname == 'CRITICAL':
            record.levelname = 'CRIT'

        log_message = super().format(record)
        log_level_color = self.COLOR_MAP.get(record.levelname, colorama.Fore.WHITE)
        log_message = f"[{record.created:.1f}s] {log_level_color}[{record.levelname}]{colorama.Style.RESET_ALL}\t- {log_message}"
        return log_message

time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
output_handler = logging.StreamHandler(sys.stdout)
output_handler.setFormatter(ColoredFormatter())
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.addHandler(output_handler)

TOKEN  = os.environ['DISCORD_TOKEN']
PASSWD = os.environ['PASSWD']
DBUSER = os.environ['DBUSER']
DBPASS = os.environ['DBPASS']
DBHOST = os.environ['DBHOST']
LVHOST = os.environ['LVHOST']
SPCLNT = os.environ['SPCLNT']
SPSECR = os.environ['SPSECR']


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


time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
bot = Bot(commands_prefix = "sc.", intents=discord.Intents.all())
conn = psycopg2.connect(
        host = DBHOST,
        database = "nextmdb",
        user = DBUSER,
        password = DBPASS)
logger.info("Connected to PSQL database")

if not os.path.exists('logs'):
    os.mkdir('logs')


if None in [TOKEN, PASSWD, DBHOST, DBPASS, DBUSER]:
    raise(FileError('.env', 'corrupt'))
logger.info("Files checked")


# Bot configuration
@bot.event
async def on_ready():
    guilds = [guild.id for guild in bot.guilds]
    await bot.add_cog(music_cog(bot, conn, guilds, logger))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Link, start.."))
    bot.dispatch("guilds_autosync")

    sc = spotify.SpotifyClient(
        client_id=SPCLNT,
        client_secret=SPSECR
    )

    node: wavelink.Node = wavelink.Node(uri=f'http://{LVHOST}', password=PASSWD)
    await wavelink.NodePool.connect(client=bot, nodes=[node], spotify=sc)
    logger.info("Bot ready")
    

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    logger.info(f"Node \x1b[39;1mID: {node.id}\x1b[39;0m ready.")


@bot.command()
async def inspect(ctx):
    await ctx.send(embed=embeds.default())

if __name__ == "__main__":
    bot.run(TOKEN, log_handler=None)
