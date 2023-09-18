print("AT PROJECT Limited, 2022 - 2023; AT_nEXT-v2.3")
print("Product licensed by CC BY-NC-ND-4, file `LICENSE`")
print("The license applies to all project files and previous versions (commits)")
try:
    print("\tImporting libraries...")
    import os
    import json
    import logging
    from datetime import datetime
    
    import discord
    from discord.ext import commands
    import psycopg2
    import wavelink
    from wavelink.ext import spotify
    from dotenv import load_dotenv

    import embeds
    from music import music_cog
    from exceptions import FileError
    print("[ \x1b[32;1mOK\x1b[39;0m ] Libraries imported")
except Exception as exception:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Importing libraries...")
    raise exception

# Some checks

print('\tChecking files...')
if not os.path.exists('files'):
    print("\t `logs` dir not found, creating...")
    os.mkdir('logs')
print("[ \x1b[32;1mOK\x1b[39;0m ]  Checked `files/`")

if not os.path.isfile('files/config.json'):
    print('Config file not found, creating...')
    def_config = { "logging" : False, "music" : True }
    with open('files/config.json', 'w') as f:
        f.seek(0)
        json.dump(def_config, f, indent=4, ensure_ascii=False)
        f.truncate()
print("[ \x1b[32;1mOK\x1b[39;0m ]  Checked `config.json`")

if not os.path.exists('logs'):
    print("\t `logs` dir not found, creating...")
    os.mkdir('logs')
print("[ \x1b[32;1mOK\x1b[39;0m ]  Checked `logs/`")

if not os.path.isfile('.env'):
    raise(FileError('.env', 'notfound'))
print("[ \x1b[32;1mOK\x1b[39;0m ]  Checked `.env`")

# Env and config loading
load_dotenv()
TOKEN  = os.getenv('DISCORD_TOKEN')
PASSWD = os.getenv('PASSWD')
DBUSER = os.getenv('DBUSER')
DBPASS = os.getenv('DBPASS')
DBHOST = os.getenv('DBHOST')
SPCLNT = os.getenv('SPCLNT')
SPSECR = os.getenv('SPSECR')

# Connecting to DB
print("\tConnecting to PSQL DB...")
conn = psycopg2.connect(
    host = DBHOST,
    database = "nextmdb",
    user = DBUSER,
    password = DBPASS
)

print("[ \x1b[32;1mOK\x1b[39;0m ]  Connected to PSQL DB")

if TOKEN is None or PASSWD is None or DBHOST is None or DBPASS is None or DBUSER is None:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Loading config...")
    raise(FileError('.env', 'corrupt'))

with open("files/config.json", "r") as f:
    data = json.load(f)
    logs = data["logging"]
    music = data["music"]

time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

if logs:
    handler = logging.FileHandler(filename=f'logs/{time}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    print(f"\r[ \x1b[32;1mOK\x1b[39;0m ]  Loging started to file '{time}.log'.")
else:
    print(f"\r[ \x1b[33;1mWARN\x1b[39;0m ]  Log system disabled.")
bot = commands.Bot(command_prefix = "sc.", intents=discord.Intents.all())


@bot.event
async def on_ready():
    if music:
        try:
            await bot.add_cog(music_cog(bot, time, logs, conn))
            print("\r[ \x1b[32;1mOK\x1b[39;0m ]  Music COG imported.")
        except:
            pass
    else:
        print(f"\r[ \x1b[33;1mWARN\x1b[39;0m ]  Music module disabled.")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Link, start.."))
    print("\r[ \x1b[32;1mOK\x1b[39;0m ]  Bot started.")

    if music:
        sc = spotify.SpotifyClient(
            client_id=SPCLNT,
            client_secret=SPSECR
        )
        node: wavelink.Node = wavelink.Node(uri='http://localhost:2333', password=PASSWD)
        await wavelink.NodePool.connect(client=bot, nodes=[node], spotify=sc)

    
@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"\r[ \x1b[32;1mOK\x1b[39;0m ]  Node \x1b[39;1mID: {node.id}\x1b[39;0m ready.")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(827542572868042812)

    role = discord.utils.get(member.guild.roles, name='User')
    role_bot = discord.utils.get(member.guild.roles, name="Bots")

    await member.add_roles(role)

    embed = discord.Embed(title="Welcome!", color=0xa31eff, description=f"User {member.mention} just landed to Limited server!")
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="Server statistics", value=f"Members: `{len(role.members)}`\nBots: `{len(role_bot.members)}`")

    await channel.send(embed=embed)


# Success embed
def successEmbed(text):
    embed = discord.Embed(title=None, color=0x00FF00)
    embed.add_field(name="✅ Success", value=text)

    return embed


# Bot Commands
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
        case _:
            await ctx.send(embed=embeds.default())


try:
    if logs:
        bot.run(TOKEN, log_handler=handler)
    else:
        bot.run(TOKEN)
except Exception as exception:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Starting bot...")
    raise(exception)
