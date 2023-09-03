# AT PROJECT Limited 2022 - 2023; AT_nEXT-v2.1.5
import discord

def default():
    embed = discord.Embed(title="ENTIRE command list", description="List of ALL system commands", color=0xa31eff)

    embed.add_field(name="Global COMMANDS", value="`inspect`", inline=False)
    embed.add_field(name="Music", value="`*play [p]`, ``*24/7`")
    embed.add_field(name="User list [Music]", value="`playlist [pll]`, `addtolist [atl]`, `printlist [ptl]`, `clearlist [cll]`,"
                    " `initlist [inl]`, `resendctl [rctl]`")

    embed.set_footer(text="To get more information about COMMAND, type sc.inpect <fullCommandName> \n * - command have no description")

    return embed


def resendctl():
    embed = discord.Embed(title="PLAYLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.resendctl \nAliases: `rctl`", value="Resends music control embed.")

    return embed


def playlist():
    embed = discord.Embed(title="PLAYLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.playlist <songPosition | Def: ALL> \nAliases: `pll`", value="Music package command. Playing one or all songs from saved playlist.")

    return embed


def addtolist():
    embed = discord.Embed(title="ADDTOLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.addtolist <song> \nAliases: `atl`", value="Music package command. Adding a song to user list.")

    return embed


def printlist():
    embed = discord.Embed(title="PRINTLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.printlist <page> \nAliases: `ptl`", value="Music package command. Displaying user list of songs.")

    return embed


def clearlist():
    embed = discord.Embed(title="CLEARLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.clearlist <position | Def: ALL> \nAliases: `cll`", value="Music package command. Removing item(-s) from list.")

    return embed


def initlist():
    embed = discord.Embed(title="INITLIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.initlist \nAliases: `inl`", value="Music package command. Initialazing user list.")

    return embed


def seek():
    embed = discord.Embed(title="SEEK command/Music", color=0xa31eff)

    embed.add_field(name="sc.seek <time (secs)> \nAliases: `sk`", value="Seeks track for n seconds.")

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
