# by ElCapitan, PROJECT Limited 2022
print("AT PROJECT Limited, 2022 - 2023; ATLB-v1.5.9", end="\n\n")
try:
    print("\tImporting libraries...")
    print("\t\tImporting 'discord'")
    import discord
    from discord.ext import commands
    print("\t\tImporting 'os'")
    import os
    print("\t\tImporting 'logging'")
    import logging
    print("\t\tImporting 'embeds.py'")
    import embeds
    print("\t\tImporting 'dotenv'")
    from dotenv import load_dotenv
    print("\t\tImporting 'music.py'")
    from music import music_cog
    print("\t\tImporting 'JSON'")
    from datetime import datetime
    print("\r[ \x1b[32;1mOK\x1b[39;0m ] Libraries imported.")
except Exception as exception:
    print("\r[ \x1b[31;1mERR\x1b[39;0m ] Importing libraries...")
    print(exception)



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
handler = logging.FileHandler(filename=f'logs\{time}.log', encoding='utf-8', mode='w')
print(f"\r[ \x1b[32;1mOK\x1b[39;0m ] Loging started at file '{time}.log'")
bot = commands.Bot(command_prefix = "sc.", intents=discord.Intents.all())
bot.remove_command('help')

client = discord.Client(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("\r[ \x1b[32;1mOK\x1b[39;0m ] Bot started.")
    await bot.add_cog(music_cog(bot))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Link, start.."))


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='User')
    await member.add_roles(role)

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
        case "clearchat":
            await ctx.send(embed=embeds.clearchat())
        case "closechat":
            await ctx.send(embed=embeds.closechat())
        case "openchat":
            await ctx.send(embed=embeds.openchat())
        case "clearqueue":
            await ctx.send(embed=embeds.clearqueue())
        case "loop":
            await ctx.send(embed=embeds.loop())
        case _:
            await ctx.send(embed=embeds.default())


@bot.command()
async def ban(ctx, user: discord.User = None, reason=None, deleteMassageDays = 0):
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


@bot.command()
async def unban(ctx, user: discord.User = None):
    if user == None:
        await inspect(ctx, command="unban")
    elif ctx.message.author.guild_permissions.administrator:
        await ctx.guild.unban(user=user)
        await ctx.send(embed=successEmbed(f'***User @{user.name} successfully unbanned!***'))
    else:
        await ctx.send(embed=embeds.errorEmbed())


@bot.command()
async def clear(ctx, number=None):
    if number == None:
        await inspect(ctx, command="clearchat")
    elif ctx.message.author.guild_permissions.manage_messages:
        mgs = []
        number = int(number) + 1
        async for x in ctx.channel.history(limit = number):
            mgs.append(x)
        await ctx.channel.delete_messages(mgs)
    else:
        await ctx.send(embed=embeds.errorEmbed())


@bot.command()
async def closechat(ctx):
    if ctx.message.author.guild_permissions.manage_messages:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=successEmbed(f'Chat successfully **closed**'))
    else:
        await ctx.send(embed=embeds.errorEmbed())


@bot.command()
async def openchat(ctx):
    if ctx.message.author.guild_permissions.manage_messages:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=successEmbed(f'Chat successfully **opened**'))
    else:
        await ctx.send(embed=embeds.errorEmbed())

try:
    bot.run(TOKEN, log_handler=handler)
except Exception as exeption:
    print("\r[ \x1b[31;1mERR\x1b[39;49m ] Starting bot...")
    print(exception)
    quit(1)