# by ElCapitan, PROJECT Limited 2022
print("AT PROJECT Limited, 2022 - 2023; ATLB-v1.7.2")
try:
    print("\tImporting libraries...")
    import discord
    from discord.ext import commands
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'discord'")
    import os
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'os'")
    import wavelink
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'wavelink'")
    import logging
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'logging'")
    import embeds
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'embeds.py'")
    from dotenv import load_dotenv
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'dotenv'")
    from music import music_cog
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'music.py'")
    from datetime import datetime
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'datetime'")
    import json
    print("[ \x1b[32;1mOK\x1b[39;0m ]  Imported 'JSON'")
    print("\tLibraries imported.")
except Exception as exception:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Importing libraries...")
    print(f"\t\x1b[39;1m{exception}\x1b[39;0m")
    quit(1)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASSWD = os.getenv('PASSWD')

with open("config.json", "r") as f:
    data = json.load(f)
    logs = data["logging"]
    music = data["music"]

time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

if logs:
    handler = logging.FileHandler(filename=f'logs\{time}.log', encoding='utf-8', mode='w')
    print(f"\r[ \x1b[32;1mOK\x1b[39;0m ]  Loging started to file '{time}.log'.")
else:
    print(f"\r[ \x1b[33;1mWARN\x1b[39;0m ]  Log system disabled.")
bot = commands.Bot(command_prefix = "sc.", intents=discord.Intents.all())
bot.remove_command('help')

client = discord.Client(intents=discord.Intents.all())


@bot.event
async def on_ready():
    if music:
        await bot.add_cog(music_cog(bot, time))
        print("\r[ \x1b[32;1mOK\x1b[39;0m ]  Music COG imported.")
    else:
        print(f"\r[ \x1b[33;1mWARN\x1b[39;0m ]  Music module disabled.")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Link, start.."))
    print("\r[ \x1b[32;1mOK\x1b[39;0m ]  Bot started.")

    await wavelink.NodePool.create_node(bot=bot,
                                    host='localhost',
                                    port=2333,
                                    password=PASSWD)


@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f"\r[ \x1b[32;1mOK\x1b[39;0m ]  Node \x1b[39;1m{node}\x1b[39;0m ready.")

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track):
    print(track)


@bot.event
async def on_voice():
        print('reason')

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
        case "ban":
            await ctx.send(embed=embeds.ban())
        case "unban":
            await ctx.send(embed=embeds.unban())
        case "clear":
            await ctx.send(embed=embeds.clearchat())
        case "closechat":
            await ctx.send(embed=embeds.closechat())
        case "openchat":
            await ctx.send(embed=embeds.openchat())
        case "clearqueue":
            await ctx.send(embed=embeds.clearqueue())
        case "loop":
            await ctx.send(embed=embeds.loop())
        case "list":
            await ctx.send(embed=embeds.queue())
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
        case _:
            await ctx.send(embed=embeds.default())


@bot.command()
async def ban(ctx, user: discord.User = None, reason=None, deleteMassageDays = 0):
    try:
        if user == None:
            await inspect(ctx, command="ban")
        elif ctx.message.author.guild_permissions.ban_members:
            if reason == None:
                rsn = "No reason given"
            else:
                rsn = f'Reason: {reason}'
            try:
                await ctx.guild.ban(user=user, reason=reason, delete_message_days=deleteMassageDays)
                await ctx.send(embed=successEmbed(f'***User @{user.name} successfully banned!*** {rsn}'))
            except:
                await ctx.send(embed=embeds.errorEmbed2())
        else:
            await ctx.send(embed=embeds.errorEmbed())
    except Exception as exc:
        print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
        print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
        await ctx.send(embed=embeds.unknownError())


@bot.command()
async def unban(ctx, user: discord.User = None):
    try:
        if user == None:
            await inspect(ctx, command="unban")
        elif ctx.message.author.guild_permissions.administrator:
            await ctx.guild.unban(user=user)
            await ctx.send(embed=successEmbed(f'***User @{user.name} successfully unbanned!***'))
        else:
            await ctx.send(embed=embeds.errorEmbed())
    except Exception as exc:
        print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
        print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
        await ctx.send(embed=embeds.unknownError())


@bot.command()
async def clear(ctx, number=None):
    try:
        if number == None:
            await inspect(ctx, command="clearchat")
        elif ctx.message.author.guild_permissions.manage_messages:
            mgs = []
            number = int(number) + 1
            async for x in ctx.channel.history(limit = number):
                mgs.append(x)
            try:
                await ctx.channel.delete_messages(mgs)
            except Exception as exc:
                print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
                print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
                await ctx.send(embed=embeds.errorEmbedCustom(855, "Messages can`t be deleted!", "You are trying to delete messages, that was sended more than 2 week ago!"))
        else:
            await ctx.send(embed=embeds.errorEmbed())
    except Exception as exc:
        print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
        print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
        await ctx.send(embed=embeds.unknownError())


@bot.command()
async def closechat(ctx):
    try:
        if ctx.message.author.guild_permissions.manage_messages:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(embed=successEmbed(f'Chat successfully **closed**'))
        else:
            await ctx.send(embed=embeds.errorEmbed())
    except Exception as exc:
        print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
        print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
        await ctx.send(embed=embeds.unknownError())


@bot.command()
async def openchat(ctx):
    try:
        if ctx.message.author.guild_permissions.manage_messages:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(embed=successEmbed(f'Chat successfully **opened**'))
        else:
            await ctx.send(embed=embeds.errorEmbed())
    except Exception as exc:
        print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
        print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
        await ctx.send(embed=embeds.unknownError())

try:
    if logs:
        bot.run(TOKEN, log_handler=handler)
    else:
        bot.run(TOKEN)
except Exception as exeption:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Starting bot...")
    print(f"\t\x1b[39;1m{exeption}\x1b[39;0m")
    quit(1)