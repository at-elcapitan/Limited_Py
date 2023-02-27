# AT PROJECT Limited 2022 - 2023; ATLB-v1.7.2
import discord

def default():
    embed = discord.Embed(title="ENTIRE command list", description="List of ALL system commands", color=0xa31eff)

    embed.add_field(name="Global COMMANDS", value="`inspect`", inline=False)
    embed.add_field(name="Work with chat", value="`clear`, `closechat`, `openchat`", inline=False)
    embed.add_field(name="Work with user", value="`ban`, `unban`", inline=False)
    embed.add_field(name="Music", value="`*play [p]`, `*pause [pa]`, `*next [n, s]` `*previous [prev]`, `list [q, lst]`, `clearqueue [cq]`, `*disconnect [d]`, `loop [lp]`, `*24/7`")
    embed.add_field(name="User list [Music]", value="`playlist [pll]`, `addtolist [atl]`, `printlist [ptl]`, `clearlist [cll]`, `initlist [inl]`")

    embed.set_footer(text="To get more information about COMMAND, type sc.inpect <fullCommandName> \n * - command have no description")

    return embed

def ban():
    embed = discord.Embed(title="BAN command", description="", color=0xa31eff)

    embed.add_field(name="sc.ban <user> <reason | Def: None> <delete_message_days | Def: 0>",
                    value="Work-with-user command, using to ban user account. `[Admin-only]`", inline=False)

    return embed

def unban():
    embed = discord.Embed(title="UNBAN command", color=0xa31eff)

    embed.add_field(name="sc.unban <user>", value="Work-with-user command, using to unban user account. `[Admin-only]`")

    return embed

def clearchat():
    embed = discord.Embed(title="CLEAR command", color=0xa31eff)

    embed.add_field(name="sc.clear <value>", value="Work-with-chat command, using to clear chat. It's possible to delete up to 100 messages at a time `[From Chat-moderator]`")

    return embed

def openchat():
    embed = discord.Embed(title="OPENCHAT command", color=0xa31eff)

    embed.add_field(name="sc.openchat", value="Work-with-chat command, using to open chat for DEFAULT role. `[From Chat-moderator]`")

    return embed

def closechat():
    embed = discord.Embed(title="CLOSECHAT command", color=0xa31eff)

    embed.add_field(name="sc.closechat", value="Work-with-chat command, using to close chat for DEFAULT role. `[From Chat-moderator]`")

    return embed

def loop():
    embed = discord.Embed(title="LOOP command/Music", color=0xa31eff)

    embed.add_field(name="sc.loop <mode | Def: Change Mode [9]>\nAliases: `lp`\n", value="Loop modes: \n - Turned off [off] \n - Loop song [curr]\n - Loop queue [list]")

    return embed

def clearqueue():
    embed = discord.Embed(title="CLEAR command/Music", color=0xa31eff)

    embed.add_field(name="sc.clearqueue <position | Def: ALL> \nAliases: `cq`", value="Music package command. Used to clear part or all queue")

    return embed

def queue():
    embed = discord.Embed(title="LIST command/Music", color=0xa31eff)

    embed.add_field(name="sc.list <page | Def: POSITION> \nAliases: `q`, `lst`", value="Music package command. Displaying songs queue.")

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

# Error embed

def errorEmbed():
    embed = discord.Embed(title="System Alert: Code 871", color=0xFF0000)

    embed.add_field(name="Access Denied!",
                    value="Your your authority is not enough to use this command.", inline=False)
    
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