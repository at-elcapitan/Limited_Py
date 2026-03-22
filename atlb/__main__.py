import os
from dotenv import load_dotenv

import mafic
import discord
# import psycopg2

import utils
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
""" DBUSER = os.environ.get('DBUSER')         # PSQL database username  
DBPASS = os.environ.get('DBPASS')         # PSQL database password
DBHOST = os.environ.get('DBHOST')         # PSQL database host ip address
DBNAME = os.environ.get('DBNAME')         # PSQL database name """

bot = Bot(commands_prefix = "sc.", intents=discord.Intents.all())
host_splitted = LVHOST.split(":")

if (len(host_splitted) != 2):
    logger.critical("Unexpected lavalink host:port value")
    exit(-1)

HOST = host_splitted[0]
try:
    PORT = int(host_splitted[1])
except ValueError:
    logger.critical("Unexpected lavalink port value")
    exit(-1)

# TODO: turn on at 3.8
def db_connect():
    return None
"""     try:
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
    return conn """


@bot.event
async def on_ready():
    if ["music_cog"] not in bot.cogs.values():
        await bot.add_cog(music_cog(bot, db_connect()))

    await bot.change_presence(status=discord.Status.online, 
                              activity=discord.Game("Link, start.."))
    
    bot.dispatch("guilds_sync")

    await bot.pool.create_node(
        host=HOST,
        port=PORT,
        label="Primary",
        password=PASSWD
    )

    utils.send_postinit_message()
    

@bot.event
async def on_node_ready(node: mafic.Node):
    logger.info(f"Node Session ID: \x1b[39;1m{node.session_id}\x1b[39;0m ready.")


@bot.command()
async def inspect(ctx):
    await ctx.send(embed=embeds.default())

if __name__ == "__main__":
    if None in [TOKEN, PASSWD, LVHOST]: # , DBHOST, DBPASS, DBUSER, DBNAME
        raise(FileError('.env', 'corrupt'))
    logger.info("Files checked")

    bot.run(TOKEN, log_handler=None)
