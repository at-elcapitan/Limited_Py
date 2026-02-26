import os
from dotenv import load_dotenv

import discord
import psycopg2
import wavelink

import embeds
from exceptions import FileError
from music import music_cog
from logger import logger
from modified_bot import Bot

# Getting global variables
load_dotenv()

TOKEN  = os.environ.get('DISCORD_TOKEN')  # Discord token
PASSWD = os.environ.get('PASSWD')         # Lavalink password
LVHOST = os.environ.get('LVHOST')         # Lavalink host ip address
DBUSER = os.environ.get('DBUSER')         # PSQL database username  
DBPASS = os.environ.get('DBPASS')         # PSQL database password
DBHOST = os.environ.get('DBHOST')         # PSQL database host ip address
DBNAME = os.environ.get('DBNAME')         # PSQL database name

bot = Bot(commands_prefix = "sc.", intents=discord.Intents.all())

def db_connect():
    try:
        conn = psycopg2.connect(
            host = DBHOST,
            database = DBNAME,
            user = DBUSER,
            password = DBPASS
        )
    except psycopg2.OperationalError:
        logger.critical("Unable to connect to database")
        exit(-1)
        
    logger.info("Connected to PSQL database")
    return conn


@bot.event
async def on_ready():
    if ["music_cog"] not in bot.cogs.values():
        await bot.add_cog(music_cog(bot, db_connect()))

    await bot.change_presence(status=discord.Status.online, 
                              activity=discord.Game("Link, start.."))
    
    bot.dispatch("guilds_sync")

    node: wavelink.Node = wavelink.Node(uri=f'http://{LVHOST}', password=PASSWD)
    await wavelink.Pool.connect(client=bot, nodes=[node])

    logger.info("Bot ready")
    

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    logger.info(f"Node \x1b[39;1mID: {payload.node.identifier}\x1b[39;0m ready.")


@bot.command()
async def inspect(ctx):
    await ctx.send(embed=embeds.default())

if __name__ == "__main__":
    if None in [TOKEN, PASSWD, DBHOST, DBPASS, DBUSER, DBNAME]:
        raise(FileError('.env', 'corrupt'))
    logger.info("Files checked")

    bot.run(TOKEN, log_handler=None)
