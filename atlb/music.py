# AT PROJECT Limited 2022 - 2023; ATLB-v2.1.3.2
import math
import json
import asyncio
import logging
import datetime
import traceback

import discord
import wavelink
import messages
from discord import ui
from discord import Interaction
from discord import ButtonStyle
from discord.ext import commands
from embeds import errorEmbedCustom, eventEmbed, unknownError

class music_cog(commands.Cog):
    def __init__(self, bot, time, logs):
        self.bot = bot
        self.is_logging = logs

        if self.is_logging:
            self.logger = logging.getLogger("music_cog")
            handler = logging.FileHandler(filename=f'logs/{time}.log', encoding='utf-8', mode='a')
            self.logger.addHandler(handler)

        self.song_source = ""
        self.song_title = ""
        self.song_position = 0
        self.song_changed = False
        self.interloop = False
        self.loop = 0
        self.msg = None
        self.auto_disconnect = True
        self.command_channel = ""
        self.music_queue = []
        self.vc = None

        @bot.event
        async def on_display_song(ctx, m_url, f = False):
            await self.vc.play(m_url)

            if f and self.msg is None:
                await self.song_stats(ctx)


    def set_none_song(self):
        self.music_queue = []
        self.song_source = ""
        self.song_title = ""
        self.loop = 0
        self.song_position = 0
    
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        reason = payload.reason
        
        if reason == "STOPPED":
            self.song_changed = True

        try:
            if reason == 'FINISHED':
                ctx = player.ctx
                self.change_song(ctx)
                self.song_changed = True
        except:
            pass


    @commands.Cog.listener()
    async def on_set_none(self):
        await self.msg.edit(embed=discord.Embed(title="Music is not playing", description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ", color=0xa31eff))


    def change_song(self, ctx):
        if self.song_position == len(self.music_queue) - 1 and self.loop == 0:
            self.set_none_song()
            self.bot.dispatch("set_none")
            return
        
        if self.loop == 1:
            if self.song_position == len(self.music_queue) - 1:
                self.song_position = 0
            else:
                self.song_position += 1
            self.song_source[0] = self.music_queue[self.song_position][0]
            self.song_source[2] = self.music_queue[self.song_position][2]
            self.song_title = self.music_queue[self.song_position][0].title
        
        if self.loop == 0:
            self.song_position += 1
            self.song_source[0] = self.music_queue[self.song_position][0]
            self.song_source[2] = self.music_queue[self.song_position][2]
            self.song_title = self.music_queue[self.song_position][0].title

        if self.loop == 2:
            self.song_source[0] = self.music_queue[self.song_position][0]
            self.song_source[2] = self.music_queue[self.song_position][2]
            self.song_title = self.music_queue[self.song_position][0].title
            
        self.play_next(ctx)

    
    def play_next(self, ctx):
        try:
            m_url = self.song_source[0]
            self.bot.dispatch("display_song", ctx, m_url)

        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())


    async def play_music(self, ctx):
        m_url = self.song_source[0]

        if self.vc is None:
            self.vc: wavelink.Player = await self.song_source[1].connect(cls=wavelink.Player)

        self.vc.ctx = ctx
        self.bot.dispatch("display_song", ctx, m_url, True)


    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        try:
            query = " ".join(args)
            voice_channel = ctx.author.voice.channel

            if query == '':
                await ctx.send(embed=errorEmbedCustom(844, "Empty", "Empty request cannot be processed."))
                return
            
            song = await wavelink.YouTubeTrack.search(query)
            song = song[0]
            
            if type(song) == type(True):
                await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
                return
            
            if self.vc is None or not self.vc.is_playing():
                self.music_queue.append([song, voice_channel, ctx.author])
                self.song_source = [song, voice_channel, ctx.author]
                self.song_title = song.title
                self.command_channel = ctx.channel
                await self.play_music(ctx)
                self.song_changed = True
                return
            
            self.music_queue.append([song, voice_channel, ctx.author])
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="24/7")
    async def auto_disconnect(self, ctx):
        try:
            if not self.ac24 and ctx.author.guild_permissions.administrator:
                pass
            elif not self.ac24:
                await ctx.send(embed = errorEmbedCustom(894, "Locked", "Administrator disabled some music commands."))
                return
            
            if self.auto_disconnect:
                self.auto_disconnect = False
                embed = discord.Embed(title="✅ Mode changed", description="24/7 mode **enabled**", color=0xa31eff)
                await ctx.send(embed=embed)
            else:
                self.auto_disconnect = True
                embed = discord.Embed(title="✅ Mode changed", description="24/7 mode **disabled**", color=0xa31eff)
                await ctx.send(embed=embed)
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    # User playlist
    @commands.command(name='playlist', aliases=['pll'])
    async def import_list(self, ctx, num = 0):
        try:
            uid = str(ctx.author.id)
            voice_channel = ctx.author.voice.channel

            with open('files/lists.json', 'r', encoding="utf-8") as f:
                list = json.load(f)
                if uid in list:
                    list = list[uid]
                else: 
                    await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                    return

            if len(list) == 0:
                await ctx.send(embed=errorEmbedCustom("804.5", "Can`t read list!", "Error: your list is empty!"))
                return

            if int(num) != 0:
                item = list[int(num) - 1][1]
                song = await wavelink.YouTubeTrack.search(item)
                song = song[0]

                if not song:
                    await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{list[int(num) - 1][0]}**"))
                    return

                if self.song_source == "":
                    self.song_source = [song, voice_channel, ctx.author]
                    self.song_title = song.title
                    self.command_channel = ctx.channel
                self.music_queue.append([song, voice_channel, ctx.author])
                if self.vc is None or not self.vc.is_playing():
                    await self.play_music(ctx)
                    self.song_changed = True
                return

            for item in list:
                try:
                    song = await wavelink.YouTubeTrack.search(item[1])
                except:
                    await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{item[0]}**"))
                    continue
                song = song[0]

                if self.song_source == "":
                    self.song_source = [song, voice_channel, ctx.author]
                    self.song_title = song.title
                    if self.vc is None or not self.vc.is_playing():
                        self.music_queue.append([song, voice_channel, ctx.author])
                        await self.play_music(ctx)
                        self.song_changed = True
                else:
                    self.music_queue.append([song, voice_channel, ctx.author])
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="addtolist", aliases=['atl'])
    async def load_save(self, ctx, *args): 
        try:
            query = " ".join(args)
            song = await wavelink.YouTubeTrack.search(query)
            song = song[0]

            await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{song.title}**'))

            with open('files/lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                uid = str(ctx.author.id)

                if uid in data:
                    data[uid].append([song.title, query])
                else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="printlist", aliases=['ptl'])
    async def load_print(self, ctx, page = 1):
        try:
            with open('files/lists.json', 'r', encoding="utf-8") as f:
                data = json.load(f)
                uid = str(ctx.author.id)

                if uid in data:
                    lst = data[uid]
                    retval = ""
                    embed = discord.Embed(color=0x915AF2)

                    pages = math.ceil(len(lst) / 10 + 0.1)
                    page = int(page)

                    if page > pages or page <= 0:
                        await ctx.send(embed=errorEmbedCustom("801.7", "Incorrect Page", "Requested page is not exist."))
                        return

                    if page == 1:
                        srt, stp = 0, 9
                    else:
                        srt = 10 * (page - 1) - 1
                        stp = 10 * page - 1

                    for i in range(srt, stp):
                        if i > len(lst) - 1:
                            break

                        if len(lst[i][0]) > 65:
                            z = len(lst[i][0]) - 65
                            title = lst[i][0][:-z] + "..."
                        else:
                            title = lst[i][0]

                        retval += f"{i + 1}. " + title + "\n"
                    
                    embed.add_field(name="📄 User list", value=retval)
                    footer = f"Page: {page} of {pages}"
                    embed.set_footer(text=footer)
                    await ctx.send(embed=embed)

                else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="clearlist", aliases=['cll'])
    async def load_delete(self, ctx, num = None):
        try:
            with open('files/lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                uid = str(ctx.author.id)

                if num == None:
                    data[uid] = []
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text="Your playlist was cleared!"))
                else:
                    if uid in data:
                        a = data[uid][int(num) - 1][0]
                        await ctx.send(embed=eventEmbed(name="✅ Success!", text="Song **" + a + "** succesfully cleared!"))
                        data[uid].pop(int(num) - 1)
                    else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="initlist", aliases=['inl'])
    async def init_list(self, ctx):
        try:
            uid = str(ctx.author.id)

            with open('files/lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                
                if uid in data: 
                    await ctx.send(embed=errorEmbedCustom("805", "List exists!", "Error: you already have saved list!"))
                    return
                else:
                    data[uid] = []
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Your list have been succesfully initialized!"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())
    
    
    # Time Machine
    @commands.command(name="seek", aliases=['sk'])
    async def music_seek(self, ctx, num: float):
        try:
            if self.vc == None:
                await ctx.send(embed=errorEmbedCustom("872", "Change error", "Not connected to voice channel."))
                return


            if self.vc.is_playing():
                pos = self.vc.position + (num * 1000)
                await self.vc.seek(position=pos)
                
                if num > 60:
                    m = int(num // 60)
                    s = int(num %  60)

                    if s > 9:
                        txt = f'{m}m {s}s'
                    else:
                        txt = f'{m}m 0{s}s'
                else:
                    txt = f'{int(num)}s'
                await ctx.send(embed=eventEmbed(name="✅ Seek complete", text=f"Track **{self.song_title}** seeked for `{txt}`"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())
    

    # nEXT Update
    def gen_song_embed(self):
        song_len_formatted = datetime.datetime.fromtimestamp(self.song_source[0].length / 1000).strftime("%M:%S")
        
        embed = discord.Embed(title=f"{self.song_title}", description=f"Song length: {song_len_formatted}\n\n> URL: [youtube.com]({self.song_source[0].uri})\n> Ordered by: `{self.song_source[2]}`", color=0xa31eff)        

        match self.loop:
            case 2:
                loop_on = "current song"
            case 1:
                loop_on = "on playlist"
            case 0:
                loop_on = "turned off"

        if self.auto_disconnect:
            auto_discon = "disabled"
        else:
            auto_discon = "enabled"

        footer = f"Loop: {loop_on}\n24/7: {auto_discon}"
        embed.set_footer(text=footer)
        
        return embed


    async def song_stats(self, ctx: commands.Context):
        self.interloop = True
        view = ui.View()
        view = self.add_buttons(view, "⏸️ Pause", ["🔁", ButtonStyle.gray])

        self.msg = await ctx.send(embed=self.gen_song_embed(), view=view)
        

        while self.interloop:
            if self.song_changed:
                try: await self.msg.edit(embed=self.gen_song_embed()) 
                except: pass
                self.song_changed = False

            await asyncio.sleep(1)

        await self.msg.delete()
        self.msg = None

    
    def add_buttons(self, view, clab1: str, clab2: list) -> ui.View:
        down = ui.Button(label="🔈 Down", style=ButtonStyle.primary, custom_id = "down", row=1)
        previous = ui.Button(label="⏮️ Previous", style=ButtonStyle.primary, custom_id = "prev", row=1)
        next = ui.Button(label="⏭️ Next", style=ButtonStyle.primary, custom_id = "next", row=1)
        up = ui.Button(label="🔊 Up", style=ButtonStyle.primary, custom_id = "up", row=1)
        pause = ui.Button(label=f"{clab1}", style=ButtonStyle.primary, custom_id = "pause", row=1)
        lst = ui.Button(label="📄 Queue", style=ButtonStyle.gray, custom_id = "queue", row=2)
        loop = ui.Button(label=f"{clab2[0]} Loop", style=clab2[1], custom_id="loop", row=2)
        beg = ui.Button(label="⏪ Restart", style=ButtonStyle.gray, custom_id="beg", row=2)
        stop = ui.Button(label="⏹️ Stop", style=ButtonStyle.gray, custom_id="stop", row=2)
        cq = ui.Button(label="🧹 Clear", style=ButtonStyle.gray, custom_id="clearq", row=2)

        view.add_item(down)
        view.add_item(previous)
        view.add_item(pause)
        view.add_item(next)
        view.add_item(up)
        view.add_item(lst)
        view.add_item(cq)
        view.add_item(stop)
        view.add_item(loop)
        view.add_item(beg)

        return view


    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        if interaction.data["component_type"] == 2:
            button_id = interaction.data["custom_id"]

            if button_id == "down":
                if not self.vc.volume == 0:
                    await self.vc.set_volume(self.vc.volume - 10)
                    await interaction.response.defer()

            if button_id == "up":
                if not self.vc.volume == 150:
                    await self.vc.set_volume(self.vc.volume + 10)
                    await interaction.response.defer()

            if button_id == "pause":
                if not self.vc.is_paused():
                    await self.vc.pause()
                    self.is_playing = True

                    view = ui.View()

                    match self.loop:
                        case 0:
                            view = self.add_buttons(view, "⏸️ Resume", ["🔁", ButtonStyle.gray])
                        case 1:
                            view = self.add_buttons(view, "⏸️ Resume", ["🔁", ButtonStyle.success])
                        case 2:
                            view = self.add_buttons(view, "⏸️ Resume", ["🔂", ButtonStyle.success])

                    await interaction.response.edit_message(embed=self.gen_song_embed(), view=view)
                    return

                await self.vc.resume()

                view = ui.View()
                match self.loop:
                    case 0:
                        view = self.add_buttons(view, "⏸️ Pause", ["🔁", ButtonStyle.gray])
                    case 1:
                        view = self.add_buttons(view, "⏸️ Pause", ["🔁", ButtonStyle.success])
                    case 2:
                        view = self.add_buttons(view, "⏸️ Pause", ["🔂", ButtonStyle.success])

                await interaction.response.edit_message(embed=self.gen_song_embed(), view=view)

        if button_id == "queue":
            await self.nEXT_queue(interaction)

        if button_id == "stop":
            await self.vc.stop()
            await self.vc.disconnect()
            self.set_none_song()
            self.vc = None
            self.interloop = False
            await interaction.response.defer()

        if button_id == "clearq":
            await self.vc.stop()
            self.set_none_song()
            embed = discord.Embed(title="Music is not playing", description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ", color=0xa31eff)        
            await interaction.response.edit_message(embed=embed)

        if button_id == "loop":
            if self.loop != 2:
                self.loop += 1
            else:
                self.loop = 0
            
            view = ui.View()

            match self.loop:
                case 0:
                    view = self.add_buttons(view, "⏸️ Pause", ["🔁", ButtonStyle.gray])
                case 1:
                    view = self.add_buttons(view, "⏸️ Pause", ["🔁", ButtonStyle.success])
                case 2:
                    view = self.add_buttons(view, "⏸️ Pause", ["🔂", ButtonStyle.success])

            await interaction.response.edit_message(embed=self.gen_song_embed(), view=view)

        if button_id == "beg":
            await self.vc.seek(position=0)
            await interaction.response.defer()

        if button_id == "next":
            if self.vc != None:
                if self.loop == 1:
                    if len(self.music_queue) == 0:
                        await self.vc.stop()
                        self.set_none_song()

                    if self.song_position == len(self.music_queue):
                        self.song_position = 0

                    await self.vc.stop()
                    self.change_song(self.vc.ctx)
                    return
                
                await self.vc.stop()
                if self.loop == 2:
                    self.song_position += 1

                self.change_song(self.vc.ctx)

            await interaction.response.defer()

        if button_id == "prev":
            if self.song_position != 0:
                await self.vc.stop()
                if self.loop == 2: self.song_position -= 1
                else: self.song_position -= 2
                self.change_song(self.vc.ctx)
            else:
                await self.vc.stop()
                if self.loop == 2: self.song_position = len(self.music_queue) - 1
                else: self.song_position = len(self.music_queue) - 2
                self.change_song(self.vc.ctx)

            await interaction.response.defer()


    async def nEXT_queue(self, interaction: Interaction):
        view = messages.ListControl(self.music_queue, self.song_title)

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(self.music_queue) / 10 + 0.1)
        srt, stp = 0, 10

        for i in range(srt, stp):
            if i > len(self.music_queue) - 1:
                break
            if len(self.music_queue[i][0].title) > 65:
                z = len(self.music_queue[i][0].title) - 65
                title = self.music_queue[i][0].title[:-z] + "..."
            else:
                title = self.music_queue[i][0].title

            if self.song_title == self.music_queue[i][0].title:
                retval += "**  • " + title + "**\n"
                continue
            retval += f"{i + 1}. " + title + "\n"
            
        embed.add_field(name="📄 Playlist", value=retval)
        embed.set_footer(text=f"Page: {1} of {pages}")

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.time_stop()

        while True:
            await view.wait()
            await asyncio.sleep(1)