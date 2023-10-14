# AT PROJECT Limited 2022 - 2023; ATLB-v3.1
import discord

def default():
    embed = discord.Embed(title="ENTIRE command list", description="List of ALL system commands", color=0xa31eff)

    embed.add_field(name="Global COMMANDS", value="`sc.inspect`", inline=False)
    embed.add_field(name="Music", value="`/youtube`, `/soundcloud`, `/spotify`, `/resend_control`, `/seek`, `/clear`")
    embed.add_field(name="User list [Music]", value="`/list_add`, `/list_display`, `/list_remove`, `/list_play`")

    return embed


# Error embed
def errorEmbed():
    embed = discord.Embed(title="System Alert: Code 871", color=0xFF0000)

    embed.add_field(name="Access Denied!",
                    value="Your authority is not enough to use this command.", inline=False)
    
    return embed


def errorEmbed2():
    embed = discord.Embed(title="System Alert: Code 871", color=0xFF0000)

    embed.add_field(name="Access Denied!",
                    value="I don't have the privileges or my role isn't high enough", inline=False)
    
    return embed


def errorEmbedCustom(errorNum, name, text):
    embed = discord.Embed(title=f"System Alert: Code {errorNum}", color=0xFF0000)

    embed.add_field(name=name, value=text, inline=False)
    
    return embed


def eventEmbed(title = None, text = None, name = ""):
    embed = discord.Embed(title=title, color=0x915AF2)

    embed.add_field(name=name, value=text, inline=False)

    return embed


def unknownError():
    embed = discord.Embed(title="System Alert: Code 899", color=0xFF0000)

    embed.add_field(name="Unknown error!",
                    value="Unknown error ocurred. Please, contact administrator.", inline=False)
    
    return embed


def disconnected_embed():
    embed = discord.Embed(title="Timed out", description="Disconnected from the voice channel due to inactivity.", color=0xFF0000)
    return embed
