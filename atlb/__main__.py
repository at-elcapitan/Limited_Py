print("AT PROJECT Limited, 2022 - 2023;  ATLB-v3.1_beta")
print("Product licensed by CC BY-NC-ND-4, file `LICENSE`")
print("The license applies to all project files and previous versions (commits)")
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
from dotenv import load_dotenv

import embeds
from music import music_cog
from exceptions import FileError

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
handler = logging.FileHandler(filename=f'logs/{time}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

output_handler = logging.StreamHandler(sys.stdout)
output_handler.setFormatter(ColoredFormatter())

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logger.addHandler(output_handler)
logger.addHandler(handler)


load_dotenv()
TOKEN  = os.getenv('DISCORD_TOKEN')
PASSWD = os.getenv('PASSWD')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBHOST = os.getenv('DBHOST')
SPCLNT = os.getenv('SPCLNT')
SPSECR = os.getenv('SPSECR')


time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
bot = commands.Bot(command_prefix = "sc.", intents=discord.Intents.all())
conn = psycopg2.connect(
        host = DBHOST,
        database = "nextmdb",
        user = DBUSER,
        password = DBPASS)
logger.info("Connected to PSQL database")

if not os.path.exists('logs'):
    os.mkdir('logs')

if not os.path.isfile('.env'):
    raise(FileError('.env', 'notfound'))

if None in [TOKEN, PASSWD, DBHOST, DBPASS, DBUSER]:
    raise(FileError('.env', 'corrupt'))
logger.info("Files checked")


# Bot configuration
@bot.event
async def on_ready():
    guilds = [guild.id for guild in bot.guilds]
    await bot.add_cog(music_cog(bot, conn, guilds, logger), guilds=[discord.Object(id=guild) for guild in guilds])
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Link, start.."))
    bot.dispatch("guilds_autosync", bot.guilds)

    sc = spotify.SpotifyClient(
        client_id=SPCLNT,
        client_secret=SPSECR
    )

    node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password=PASSWD)
    await wavelink.NodePool.connect(client=bot, nodes=[node], spotify=sc)
    logger.info("Bot ready")
    

@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    logger.info(f"Node \x1b[39;1mID: {node.id}\x1b[39;0m ready.")


@bot.command()
async def inspect(ctx, command=None):
    match command:
        case "clearqueue":
            await ctx.send(embed=embeds.clearqueue())
        case "playlist":
            await ctx.send(embed=embeds.playlist())
        case "addtolist":
            await ctx.send(embed=embeds.addtolist())
        case "printlist":
            await ctx.send(embed=embeds.printlist())
        case "clearlist":
            await ctx.send(embed=embeds.clearlist())
        case "initlist":
            await ctx.send(embed=embeds.initlist())
        case "resendctl":
            await ctx.send(embed=embeds.resendctl())
        case "seek":
            await ctx.send(embed=embeds.seek())
        case "playyoutube":
            await ctx.send(embed=embeds.playyoutube())
        case "playspotify":
            await ctx.send(embed=embeds.playspotify())
        case "playsoundcloud":
            await ctx.send(embed=embeds.playsoundcloud())
        case _:
            await ctx.send(embed=embeds.default())


if __name__ == "__main__":
    bot.run(TOKEN, log_handler=handler)