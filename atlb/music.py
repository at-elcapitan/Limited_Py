# AT PROJECT Limited 2022 - 2023; AT_nEXT-v2.1.5
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
        self.loop = 0
        self.command_channel = ""
        self.music_queue = []
        self.msg = None
        self.vc = None


    # Refactored code
    def set_none_song(self):
        self.music_queue = []
        self.song_source = []
        self.song_title = ""
        self.loop = 0
        self.song_position = 0


    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args):
        query = " ".join(args)

        if query == '':
            await ctx.send(embed=errorEmbedCustom(844, "Empty", "Empty request cannot be processed."))
            return

        song = await wavelink.YouTubeTrack.search(query)
        song = song[0]
        voice_channel = ctx.author.voice.channel

        if type(song) == type(True):
            await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
            return
        
        if self.vc is None or not self.vc.is_playing():
            self.music_queue.append([song, voice_channel, ctx.author])
            self.bot.dispatch("handle_music", ctx, song)
            return
        
        self.music_queue.append([song, voice_channel, ctx.author])
        self.bot.dispatch("return_message", ctx)

    
    @commands.command("resendctl", aliases=["rctl", "rcl"])
    async def resend_song_ctl(self, ctx):
        await self.msg.delete()
        self.msg = None
        self.bot.dispatch("return_message", ctx)


    @commands.Cog.listener()
    async def on_set_none(self):
        await self.msg.edit(embed=discord.Embed(title="Music is not playing", description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ", color=0xa31eff))


    @commands.Cog.listener()
    async def on_handle_music(self, ctx: commands.Context, song, f = False):
        self.song_source = self.music_queue[self.song_position]
        self.song_title = self.song_source[0].title
        self.command_channel = ctx.channel

        if self.vc is None:
            self.vc: wavelink.Player = await self.song_source[1].connect(cls=wavelink.Player)
            self.vc.ctx = ctx

        await self.vc.play(song)
        self.bot.dispatch("return_message", ctx)

    
    @commands.Cog.listener()
    async def on_return_message(self, ctx):
        view = ui.View()

        if self.vc.is_paused():
            clab1 = "▶️ Resume"
        else:
            clab1 = "⏸️ Pause"

        match self.loop:
            case 0:
                clab2 = ["🔁", ButtonStyle.gray]
            case 1:
                clab2 = ["🔁", ButtonStyle.success]
            case 2:
                clab2 = ["🔂", ButtonStyle.success]

        items = [ 
            ui.Button(label="🔈 Down", style=ButtonStyle.primary, custom_id = "down", row=1), 
            ui.Button(label="⏮️ Previous", style=ButtonStyle.primary, custom_id = "prev", row=1),
            ui.Button(label=f"{clab1}", style=ButtonStyle.primary, custom_id = "pause", row=1),
            ui.Button(label="⏭️ Next", style=ButtonStyle.primary, custom_id = "next", row=1),
            ui.Button(label="🔊 Up", style=ButtonStyle.primary, custom_id = "up", row=1),
            ui.Button(label="📄 Queue", style=ButtonStyle.gray, custom_id = "queue", row=2),
            ui.Button(label="🧹 Clear", style=ButtonStyle.gray, custom_id="clearq", row=2),
            ui.Button(label="⏹️ Stop", style=ButtonStyle.gray, custom_id="stop", row=2),
            ui.Button(label=f"{clab2[0]} Loop", style=clab2[1], custom_id="loop", row=2),
            ui.Button(label="⏪ Restart", style=ButtonStyle.gray, custom_id="beg", row=2)
        ]

        for x in items:
            view.add_item(x)

        song_len_formatted = datetime.datetime.fromtimestamp(self.song_source[0].length / 1000).strftime("%M:%S")
        embed = discord.Embed(title=f"{self.song_title}", description=f"Song length: {song_len_formatted}\n\n> URL: [youtube.com]({self.song_source[0].uri})\n> Ordered by: `{self.song_source[2]}`", color=0xa31eff)        

        match self.loop:
            case 2:
                loop_on = "current song"
            case 1:
                loop_on = "on playlist"
            case 0:
                loop_on = "turned off"

        footer = f"Loop: {loop_on}\nPosition: {self.song_position + 1} of {len(self.music_queue)}\nVolume: {self.vc.volume}%"
        embed.set_footer(text=footer)

        if self.msg == None:
            self.msg = await ctx.send(embed=embed, view=view)
            return
        
        await self.msg.edit(embed=embed, view=view)


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        reason = payload.reason

        if reason == "STOPPED" and not self.vc == None and len(self.music_queue) != 0:
            self.bot.dispatch("return_message", self.vc.ctx)

        try:
            if reason == 'FINISHED':
                ctx = player.ctx
                self.change_song(ctx)
        except:
            pass


    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        if interaction.data["component_type"] != 2:
            return
        
        button_id = interaction.data["custom_id"]

        if button_id == "down":
            if not self.vc.volume == 0:
                await self.vc.set_volume(self.vc.volume - 10)
                self.bot.dispatch("return_message", self.vc.ctx)
                await interaction.response.defer()

        if button_id == "up":
            if not self.vc.volume == 150:
                await self.vc.set_volume(self.vc.volume + 10)
                self.bot.dispatch("return_message", self.vc.ctx)
                await interaction.response.defer()

        if button_id == "pause":
            if not self.vc.is_paused():
                await self.vc.pause()
                self.is_playing = True

                self.bot.dispatch("return_message", self.vc.ctx)
                return

            await self.vc.resume()
            self.bot.dispatch("return_message", self.vc.ctx)


        if button_id == "queue":
            await self.nEXT_queue(interaction)

        if button_id == "stop":
            await self.vc.stop()
            await self.vc.disconnect()
            self.set_none_song()
            self.vc = None
    
            await self.msg.delete()
            self.msg = None
            
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
            
            self.bot.dispatch("return_message", self.vc.ctx)
            await interaction.response.defer()

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
                    await interaction.response.defer()
                    return
                
                await self.vc.stop()
                if self.loop == 2:
                    self.song_position += 1

                self.change_song(self.vc.ctx)

            self.bot.dispatch("return_message", self.vc.ctx)
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

            self.bot.dispatch("return_message", self.vc.ctx)
            await interaction.response.defer()


    # Commands
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
        
        if self.loop == 0:
            self.song_position += 1
        
        self.bot.dispatch("handle_music", ctx, self.music_queue[self.song_position][0])

    
    async def nEXT_queue(self, interaction: Interaction):
        view = messages.ListControl(self.music_queue, self.song_title)

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(self.music_queue) / 10 + 0.1)
        srt, stp = 0, 9

        for i in range(srt, stp):
            if i > len(self.music_queue) - 1:
                break
            if len(self.music_queue[i][0].title) > 65:
                z = len(self.music_queue[i][0].title) - 65
                title = self.music_queue[i][0].title[:-z] + "..."
            else:
                title = self.music_queue[i][0].title

            if self.song_title == self.music_queue[i][0].title:
                retval += f"**{i + 1}. " + title + "\n**"
                continue
            retval += f"{i + 1}. " + title + "\n"
            
        embed.add_field(name="📄 Playlist", value=retval)
        embed.set_footer(text=f"Page: {1} of {pages}")

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.time_stop()

        while True:
            await view.wait()
            await asyncio.sleep(1)


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
            if self.is_logging:
                self.logger.warning(traceback.format_exc())
            else:
                print(traceback.format_exc())
            await ctx.send(embed=unknownError())


    # Userlist
    @commands.command(name="printlist", aliases=['ptl'])
    async def load_print(self, ctx, page = 1):
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


    @commands.command(name="clearlist", aliases=['cll'])
    async def load_delete(self, ctx, num = None):
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


    @commands.command(name="initlist", aliases=['inl'])
    async def init_list(self, ctx):
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


    @commands.command(name="addtolist", aliases=['atl'])
    async def load_save(self, ctx, *args):
        query = " ".join(args)
        song = await wavelink.YouTubeTrack.search(query)
        song = song[0]

        await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{song.title}**'))

        with open('files/lists.json', 'r+', encoding="utf-8") as f:
            data = json.load(f)
            uid = str(ctx.author.id)

            if uid in data:
                data[uid].append([song.title, song.uri])
            else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()

    
    @commands.command(name='playlist', aliases=['pll'])
    async def import_list(self, ctx, num = 0):
        uid = str(ctx.author.id)
        voice_channel = ctx.author.voice.channel

        with open('files/lists.json', 'r', encoding="utf-8") as f:
            lst = json.load(f)
            if uid in lst:
                lst = lst[uid]
            else: 
                await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
                return

        if len(lst) == 0:
            await ctx.send(embed=errorEmbedCustom("804.5", "Can`t read list!", "Error: your list is empty!"))
            return

        if int(num) != 0:
            item = lst[int(num) - 1][1]
            
            try:
                song = await wavelink.YouTubeTrack.search(item[1])
                song = song[0]
            except:
                await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{item[0]}**"))
                return

            if not song:
                await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{lst[int(num) - 1][0]}**"))
                return

            self.music_queue.append([song, voice_channel, ctx.author])
            self.bot.dispatch("return_message", ctx)

            if self.vc is None or not self.vc.is_playing():
                self.bot.dispatch("handle_music", ctx, song)

            return

        for item in lst:
            try:
                song = await wavelink.YouTubeTrack.search(item[1])
                song = song[0]
            except:
                await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{item[0]}**"))
                continue

            if self.vc is None or not self.vc.is_playing():
                self.music_queue.append([song, voice_channel, ctx.author])
                self.bot.dispatch("handle_music", ctx, song)
            else:
                self.music_queue.append([song, voice_channel, ctx.author])

        self.bot.dispatch("return_message", ctx)