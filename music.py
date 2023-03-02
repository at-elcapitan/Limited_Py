# AT PROJECT Limited 2022 - 2023; ATLB-v1.7.5
import math
import discord
import json
import asyncio
import logging
import wavelink
import traceback
from discord.ext import commands
from embeds import errorEmbedCustom, eventEmbed, unknownError, disconnected_embed, errorEmbed

class music_cog(commands.Cog):
    def __init__(self, bot, time):
        self.bot = bot

        self.logger = logging.getLogger("music_cog")
        handler = logging.FileHandler(filename=f'logs\{time}.log', encoding='utf-8', mode='a')
        self.logger.addHandler(handler)

        self.is_playing = False
        self.is_paused = False
        self.song_source = ""
        self.song_title = ""
        self.song_position = 0
        self.loop = 0
        self.delay_time = 300
        self.auto_disconnect = True
        self.command_channel = ""

        self.ac24 = True
        self.acseek = True
        self.acvolume = "def"

        self.music_queue = []
        self.vc = None

        @bot.event
        async def on_display_song(self, ctx, m_url, printa = True):
            if printa and self.loop != 1:
                await ctx.send(embed=eventEmbed(name="🎵   Now playing", text= f'**{self.song_title}**'))
            await self.vc.play(m_url)
            
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason: str):
        try:
            if reason == 'FINISHED':
                ctx = player.ctx
                self.change_song(ctx)
        except Exception as e:
            print(e)

    def set_none_song(self):
        self.music_queue = []
        self.is_playing = False
        self.song_source = ""
        self.song_title = ""
        self.song_position = 0
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0

            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                elif not self.auto_disconnect:
                    time = 0
                elif time == self.delay_time:
                    await voice.disconnect()
                    self.set_none_song()
                    await self.command_channel.send(embed = disconnected_embed())
                elif not voice.is_connected():
                    break


    def change_song(self, ctx):
        if len(self.music_queue) > 0:
            if self.song_position == len(self.music_queue) - 1 and self.loop == 0:
                self.set_none_song()
                return
            if self.loop == 0:
                self.song_position += 1
                self.song_source[0] = self.music_queue[self.song_position][0]
                self.song_title = self.music_queue[self.song_position][0].title
            elif self.loop == 2:
                if self.song_position == len(self.music_queue) - 1:
                    self.song_position = 0
                else:
                    self.song_position += 1
                self.song_source[0] = self.music_queue[self.song_position][0]
                self.song_title = self.music_queue[self.song_position][0].title
            self.play_next(ctx)
        else:
            if self.loop == 1:
                self.play_next(ctx)
            elif self.loop == 2:
                self.play_next(ctx)
            else:
                self.set_none_song()


    def play_next(self, ctx):
        try:
            self.is_playing = True

            m_url = self.song_source[0]

            if not self.loop == 1:
                self.bot.dispatch("display_song", self, ctx, m_url, False)
            self.bot.dispatch("display_song", self, ctx, m_url)
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())


    async def play_music(self, ctx):
        self.is_playing = True

        m_url = self.song_source[0]

        if self.vc == None or not self.vc.is_connected():
            self.vc: wavelink.Player = await self.song_source[1].connect(cls=wavelink.Player)

            if self.vc == None:
                await ctx.send(embed=errorEmbedCustom("872", "Connect error", "Could not connect to the voice channel"))
                return
        else:
            await self.vc.move_to(self.song_source[1])

        self.vc.ctx = ctx
        self.bot.dispatch("display_song", self, ctx, m_url)


    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        try:
            query = " ".join(args)

            voice_channel = ctx.author.voice.channel
            if self.is_paused:
                await self.vc.resume()
                self.is_playing = True
                self.is_paused = False
                return
            
            if query == '':
                await ctx.send(embed=errorEmbedCustom(844, "Empty", "Empty request cannot be processed."))
                return
            song = await wavelink.YouTubeTrack.search(query=query, return_first=True)

            if type(song) == type(True):
                await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
            else:
                if not self.is_playing:
                    self.music_queue.append([song, voice_channel])
                    self.song_source = [song, voice_channel]
                    self.song_title = song.title
                    self.command_channel = ctx.channel
                    await self.play_music(ctx)
                else:
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the queue \n **{song.title}**'))
                    self.music_queue.append([song, voice_channel])
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())
    

    @commands.command(name="list", aliases=["q", "lst"])
    async def queue(self, ctx, page = None):
        try:
            retval = ""
            embed = discord.Embed(color=0x915AF2)

            pages = math.ceil(len(self.music_queue) / 10 + 0.1)
            if page == None:
                page = math.ceil((self.song_position + 1) / 10 + 0.1)
            else:
                page = int(page)

            if page > pages or page <= 0:
                await ctx.send(embed=errorEmbedCustom("801.9", "Incorrect Page", "Requested page is not exist or playlist is empty."))
                return

            if page == 1:
                srt, stp = 0, 10
            else:
                srt = 10 * (page - 1)
                stp = 10 * page

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
            
            match self.loop:
                case 1:
                    loop_on = "current song"
                case 2:
                    loop_on = "on playlist"
                case 0:
                    loop_on = "turned off"

            if self.auto_disconnect:
                auto_discon = "disabled"
            else:
                auto_discon = "enabled"
            footer = f"Page: {page} of {pages}\nLoop: {loop_on}\n24/7: {auto_discon}"
            embed.set_footer(text=footer)

            await ctx.send(embed = embed)
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="pause", aliases=["pa"])
    async def pause(self, ctx, *args):
        try:
            if self.is_playing:
                self.is_playing = False
                self.is_paused = True
                await self.vc.pause()
            elif self.is_paused:
                self.is_paused = False
                self.is_playing = True
                await self.vc.resume()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())
    

    @commands.command(name="prev", aliases=['pr'])
    async def prev_song(self, ctx):
        try:
            if self.song_position != 0:
                await self.vc.stop()
                self.song_position -= 2
                self.change_song(ctx)
            else:
                await self.vc.stop()
                self.song_position = len(self.music_queue) - 2
                self.change_song(ctx)
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="next", aliases=["n", "s"])
    async def next(self, ctx):
        try:
            if self.vc != None:
                if self.loop == 2:
                    if len(self.music_queue) == 0:
                        await self.vc.stop()
                        self.loop = 0
                        self.is_playing = False
                        self.song_source = ""
                        self.song_title = ""
                        self.song_position = 0
                    if self.song_position == len(self.music_queue):
                        self.song_position = 0
                    await self.vc.stop()
                    self.change_song(ctx)
                else:
                    await self.vc.stop()
                    self.change_song(ctx)
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())

    
    @commands.command(name="disconnect", aliases=["d"])
    async def dc(self, ctx):
        try:
            self.is_playing = False
            self.is_paused = False
            await self.vc.disconnect()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="clearqueue", aliases=["cq"])
    async def clear(self, ctx, num = None):
        try:
            if num == None:
                if self.vc != None and self.vc.is_playing():
                    await self.vc.stop()
                self.set_none_song()
                self.loop = 0
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Queue cleared"))
            else:
                title = self.music_queue[int(num) - 1][0].title
                if title == self.song_title:
                    self.vc.stop()
                    self.change_song(ctx)
                self.music_queue.pop(int(num) - 1)
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Song **" + title + "** succesfully cleared!"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())
        
        
    @commands.command(name='loop', aliases=["lp"])
    async def loop(self, ctx, mode = "9"):
        try:
            match mode:
                case "curr":
                    self.loop = 1
                    await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned on current song."))
                case "list":
                    self.loop = 2
                    await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned on playlist."))
                case "off":
                    self.loop = 0
                    await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned off."))
                case "9":
                    match self.loop:
                        case 0:
                            self.loop += 1
                            await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned on current song."))
                        case 1:
                            self.loop += 1
                            await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned on playlist."))
                        case 2:
                            self.loop = 0
                            await ctx.send(embed=eventEmbed(name="🔵 Mode changed", text="Loop turned off."))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
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
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    # User playlist
    @commands.command(name='playlist', aliases=['pll'])
    async def import_list(self, ctx, num = 0):
        try:
            id = str(ctx.author.id)
            voice_channel = ctx.author.voice.channel

            with open('lists.json', 'r', encoding="utf-8") as f:
                list = json.load(f)
                if id in list:
                    list = list[id]
                else: 
                    await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                    return

            if len(list) == 0:
                await ctx.send(embed=errorEmbedCustom("804.5", "Can`t read list!", "Error: your list is empty!"))
                return

            if int(num) != 0:
                item = list[int(num) - 1][1]
                song = await wavelink.YouTubeTrack.search(query=item, return_first=True)

                if not song:
                    await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{list[int(num) - 1][0]}**"))
                    return

                if self.song_source == "":
                    self.song_source = [song, voice_channel]
                    self.song_title = song.title
                    self.command_channel = ctx.channel
                self.music_queue.append([song, voice_channel])
                if not self.is_playing:
                    await self.play_music(ctx)
                await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the queue \n **{song.title}**'))
                return

            for item in list:
                song = await wavelink.YouTubeTrack.search(query=item[1], return_first=True)

                if not song:
                    await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{item[0]}**"))
                    continue

                if self.song_source == "":
                    self.song_source = [song, voice_channel]
                    self.song_title = song.title
                    if not self.is_playing:
                        self.music_queue.append([song, voice_channel])
                        await self.play_music(ctx)
                    await ctx.send(embed=eventEmbed(name="🔵 Processing...", text="List import process started, please wait..."))
                else:
                    self.music_queue.append([song, voice_channel])
            
            await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Track list succesfully imported!'))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="addtolist", aliases=['atl'])
    async def load_save(self, ctx, *args): 
        try:
            query = " ".join(args)
            song = await wavelink.YouTubeTrack.search(query=query, return_first=True)

            await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{song.title}**'))

            with open('lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                id = str(ctx.author.id)

                if id in data:
                    data[id].append([song.title, query])
                else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="printlist", aliases=['ptl'])
    async def load_print(self, ctx, page = 1):
        try:
            with open('lists.json', 'r', encoding="utf-8") as f:
                data = json.load(f)
                id = str(ctx.author.id)

                if id in data:
                    lst = data[id]
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
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())

    @commands.command(name="clearlist", aliases=['cll'])
    async def load_delete(self, ctx, num = None):
        try:
            with open('lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                id = str(ctx.author.id)

                if num == None:
                    data[id] = []
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text="Your playlist was cleared!"))
                else:
                    if id in data:
                        a = data[id][int(num) - 1][0]
                        await ctx.send(embed=eventEmbed(name="✅ Success!", text="Song **" + a + "** succesfully cleared!"))
                        data[id].pop(int(num) - 1)
                    else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())

    @commands.command(name="initlist", aliases=['inl'])
    async def init_list(self, ctx):
        try:
            id = str(ctx.author.id)

            with open('lists.json', 'r+', encoding="utf-8") as f:
                data = json.load(f)
                
                if id in data: 
                    await ctx.send(embed=errorEmbedCustom("805", "List exists!", "Error: you already have saved list!"))
                    return
                else:
                    data[id] = []
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.truncate()
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Your list have been succesfully initialized!"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())
    
    
    # Time Machine
    @commands.command(name="restart", aliases=['rt'])
    async def from_beginning(self, ctx):
        if self.vc.is_playing:
            await self.vc.seek(position=0)
            await ctx.send(embed=eventEmbed(name="✅ Moved", text="Song seeked to beginning."))


    @commands.command(name="seek", aliases=['sk'])
    async def music_seek(self, ctx, num: float):
        try:
            if self.vc == None:
                await ctx.send(embed=errorEmbedCustom("872", "Change error", "Not connected to voice channel."))
                return
            
            if not self.acseek and ctx.author.guild_permissions.administrator:
                pass
            elif not self.ac24:
                await ctx.send(embed = errorEmbedCustom(894, "Locked", "Administrator disabled some music commands."))
                return
            
            if self.vc.is_playing:
                pos = (self.vc.position + num) * 1000
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
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())


    @commands.command(name="volume", aliases=['vl'])
    async def volume(self, ctx, num: int):
        try:
            if self.vc == None:
                await ctx.send(embed=errorEmbedCustom("872", "Change error", "Not connected to voice channel."))
                return

            if self.acseek == "lock" and ctx.author.guild_permissions.administrator:
                pass
            elif not self.ac24:
                await ctx.send(embed = errorEmbedCustom(894, "Locked", "Administrator disabled some music commands."))
                return
            
            if self.acseek == "def":
                value = 150
            else:
                value = 1000

            if num > value or num <= 0:
                await ctx.send(embed=errorEmbedCustom(831, "Not correct value", f"Can\`t set volume to `{num}%`"))
                return
            
            if self.vc.is_playing:
                await self.vc.set_volume(num)
                await ctx.send(embed=eventEmbed(name="✅ Volume changed", text=f"Volume set to `{num}%`"))
        except Exception as exc:
            print("\r[ \x1b[31;1mERR\x1b[39;0m ]  Error occurred while executing command.")
            print(f"\t\x1b[39;1m{exc}\x1b[39;0m")
            self.logger.warning(traceback.format_exc())
            await ctx.send(embed=unknownError())

    @commands.command(name="lock")
    async def lock_admin(self, ctx, cmd = None):
        if ctx.author.guild_permissions.administrator:
            match cmd:
                case "all":
                    self.ac24 = False
                    self.acseek = False
                    self.acvolume = "lock"
                    await ctx.send(embed=eventEmbed("Command Locked", "Target: ALL", "All music commands locked for users."))
                case "24/7":
                    self.ac24 = False
                    await ctx.send(embed=eventEmbed("Command Locked", "Target: 24/7", "24/7 command disabled."))
                case "seek":
                    self.acseek = False
                    await ctx.send(embed=eventEmbed("Command Locked", "Target: SEEK", "Seek command disabled."))
                case "volume":
                    self.acvolume = "lock"
                    await ctx.send(embed=eventEmbed("Command Locked", "Target: VOLUME", "Volume command disabled."))
                case "volumemax":
                    self.acvolume = "def"
                    await ctx.send(embed=eventEmbed("Command Changed", "Target: VOLUME", "Volume atr `max` disabled."))
                case _:
                    await ctx.send(embed=eventEmbed("Error", "Locked: Nonde", "Lock target was not passed."))
        else:
            await ctx.send(embed=errorEmbed)

    @commands.command(name="unlock")
    async def unlock_admin(self, ctx, cmd = None):
        if ctx.author.guild_permissions.administrator:
            match cmd:
                case "all":
                    self.ac24 = True
                    self.acseek = True
                    self.acvolume = "def"
                    await ctx.send(embed=eventEmbed("Command Unlocked", "Target: ALL", "All music commands unlocked for users."))
                case "24/7":
                    self.ac24 = True
                    await ctx.send(embed=eventEmbed("Command Unlocked", "Target: 24/7", "24/7 command enabled."))
                case "seek":
                    self.acseek = True
                    await ctx.send(embed=eventEmbed("Command Unlocked", "Target: SEEK", "Seek command enabled."))
                case "volume":
                    self.acvolume = "def"
                    await ctx.send(embed=eventEmbed("Command Unlocked", "Target: VOLUME", "Volume command enabled."))
                case "volumemax":
                    self.acvolume = "max"
                    await ctx.send(embed=eventEmbed("Command Unlocked", "Target: VOLUME", "Volume command enabled, atr `max`."))
                case _:
                    await ctx.send(embed=eventEmbed("Error", "Locked: Nonde", "Lock target was not passed."))
        else:
            await ctx.send(embed=errorEmbed)