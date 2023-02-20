# AT PROJECT Limited 2022 - 2023; ATLB-v1.6.2_6
import discord

def default():
    embed = discord.Embed(title="ENTIRE command list", description="List of ALL system commands", color=0xa31eff)

    embed.add_field(name="Global COMMANDS", value="`inspect`", inline=False)
    embed.add_field(name="Work with chat", value="`clear`, `closechat`, `openchat`", inline=False)
    embed.add_field(name="Work with user", value="`ban`, `unban`", inline=False)
    embed.add_field(name="Music", value="`*play [p]`, `*pause [pa]`, `*skip [s]`, `*queue [q]`, `clearqueue [cq]`, `*disconnect [d]`, `loop [lp]`")
    embed.add_field(name="User list [Music]", value="`*playlist [pll]`, `addtolist [atl]`, `*printlist [ptl]`, `clearlist [cll]`, `initlist [inl]`")

    embed.set_footer(text="To get more information about COMMAND, type sc.inpect <commandName> \n * - command have no description")

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
    embed = discord.Embed(title="CLEARCHAT command", color=0xa31eff)

    embed.add_field(name="sc.clearchat <value>", value="Work-with-chat command, using to clear chat. It's possible to delete up to 100 messages at a time `[From Chat-moderator]`")

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

    embed.add_field(name="sc.loop | Short: lp", value="Music package command. Have 3 modes: \n - Turned off [0] \n - Loop queue [1] \n - Loop song [2]")

    return embed

def clearqueue():
    embed = discord.Embed(title="CLEARQUEUE command/Music", color=0xa31eff)

    embed.add_field(name="sc.cleaqueue <position | Def: ALL> | Short: q", value="Music package command. Used to clear part or all queue")

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