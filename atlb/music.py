# AT PROJECT Limited 2022 - 2023; AT_nEXT-v3.0-beta1
import math
import asyncio
import logging
import datetime
import traceback

import discord
import wavelink
from wavelink.ext import spotify
import messages
from discord import ui
from discord import Interaction
from discord import ButtonStyle
from discord.ext import commands
from embeds import errorEmbedCustom, eventEmbed, unknownError

class music_cog(commands.Cog):
    def __init__(self, bot, time, logs, connection):
        self.bot = bot
        self.is_logging = logs
        self.dbconn = connection

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
        self.server_id: int = None;
        self.msg = None
        self.vc = None


    # Refactored code
    def set_none_song(self):
        self.music_queue = []
        self.song_source = []
        self.song_title = ""
        self.loop = 0
        self.song_position = 0


    async def get_song(self, query, type: str = None):
        playlist = False

        if 'spotify.com' in query or 'spotify:track:' in query or type == 's':
            try: song = await spotify.SpotifyTrack.search(query)
            except: return None

            if len(song) == 0:
                return None
            song = song[0]

            return [song, playlist]
        
        if "soundcloud.com" in query or type == 'sc':
            if 'sets' in query:
                try: song = await wavelink.SoundCloudPlaylist.search(query)
                except: return None
                playlist = True
            else:
                try: song = await wavelink.SoundCloudTrack.search(query)
                except: return None

                if len(song) == 0:
                    return None
                song = song[0]
            
            return [song, playlist]
        
        if 'playlist' in query:
            try: song = await wavelink.YouTubePlaylist.search(query)
            except: return None
            playlist = True
        else:
            try: song = await wavelink.YouTubeTrack.search(query)
            except: return None

            if len(song) == 0:
                return None
            song = song[0]

        return [song, playlist]


    @commands.command(name="playoutube", aliases=["pyt"])
    async def play_yt(self, ctx, *args):
        query = " ".join(args)

        if query == '':
            await ctx.send(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."))
            return

        song = await self.get_song(query)
        await self.play(ctx, song)


    @commands.command(name="playsoundcloud", aliases=["psd"])
    async def play_sc(self, ctx, *args):
        query = " ".join(args)

        if query == '':
            await ctx.send(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."))
            return

        song = await self.get_song(query, 'sc')
        await self.play(ctx, song)


    @commands.command(name="playspotify", aliases=["ps"])
    async def play_sp(self, ctx, *args):
        query = " ".join(args)

        if query == '':
            await ctx.send(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."))
            return

        song = await self.get_song(query, 's')
        await self.play(ctx, song)


    async def play(self, ctx, song):
        if self.server_id == None:
            self.server_id = ctx.guild.id
        else:
            if self.server_id != ctx.guild.id:
                await ctx.send(embed=errorEmbedCustom(399.1, "VC Error", "Can't execute command. Bot already connected to other guild's channel."))
                return

        if song is None:
            await ctx.send(embed=errorEmbedCustom(854, "Not found", "Can't find song"))
            return
        
        if ctx.author.voice is None:
            await ctx.send(embed=errorEmbedCustom(399, "VC Error", "Can't get your voice channel"))
            return

        voice_channel = ctx.author.voice.channel

        if type(song) == type(True):
            await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
            return
        
        if self.vc is None or not self.vc.is_playing():
            if song[1]:
                for x in song[0].tracks: 
                    self.music_queue.append([x, voice_channel, ctx.author])
            else: self.music_queue.append([song[0], voice_channel, ctx.author])
                
            self.bot.dispatch("handle_music", ctx)
            return
        
        if song[1]: 
            for x in song[0]: self.music_queue.append([x, voice_channel, ctx.author])
        else: self.music_queue.append([song[0], voice_channel, ctx.author])
        self.bot.dispatch("return_message", ctx)

    
    @commands.command("resendctl", aliases=["rctl", "rcl"])
    async def resend_song_ctl(self, ctx):
        await self.msg.delete()
        self.msg = None
        self.bot.dispatch("return_message", ctx)


    @commands.Cog.listener()
    async def on_handle_music(self, ctx: commands.Context):
        self.song_source = self.music_queue[self.song_position]
        self.song_title = self.song_source[0].title
        self.command_channel = ctx.channel

        if self.vc is None:
            self.vc: wavelink.Player = await self.song_source[1].connect(cls=wavelink.Player)
            self.vc.ctx = ctx

        await self.vc.play(self.song_source[0])
        self.bot.dispatch("return_message", ctx)

    
    @commands.Cog.listener()
    async def on_return_message(self, ctx):
        view = ui.View()

        if self.vc.is_paused(): clab1 = "▶️ Resume" 
        else: clab1 = "⏸️ Pause"

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

        if len(self.music_queue) != 0:
            song_len_formatted = datetime.datetime.fromtimestamp(self.song_source[0].length / 1000).strftime("%M:%S")
            embed = discord.Embed(title=f"{self.song_title}", description=f"Song length: {song_len_formatted}\n\n> URL: [link]({self.song_source[0].uri})\n> Ordered by: `{self.song_source[2]}`", color=0xa31eff)        
        else:
            embed = discord.Embed(title="Music is not playing", description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ", color=0xa31eff)

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
        
        try:
            await self.msg.edit(embed=embed, view=view)
        except discord.errors.HTTPException:
            await self.msg.delete()
            self.msg = await ctx.send(embed=embed, view=view)
            



    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        reason = payload.reason

        if reason == "STOPPED" and not self.vc == None and len(self.music_queue) != 0:
            self.bot.dispatch("return_message", player.ctx)

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

        match button_id:
            case "down":
                if not self.vc.volume == 0:
                    await self.vc.set_volume(self.vc.volume - 10)
                    self.bot.dispatch("return_message", self.vc.ctx)
                    await interaction.response.defer()

            case "up":
                if not self.vc.volume == 150:
                    await self.vc.set_volume(self.vc.volume + 10)
                    self.bot.dispatch("return_message", self.vc.ctx)
                    await interaction.response.defer()

            case "pause":
                if not self.vc.is_paused():
                    await self.vc.pause()
                    self.is_playing = True

                    self.bot.dispatch("return_message", self.vc.ctx)
                    await interaction.response.defer()
                    return

                await self.vc.resume()
                self.bot.dispatch("return_message", self.vc.ctx)
                await interaction.response.defer()


            case "queue":
                await self.nEXT_queue(interaction)

            case "stop":
                await self.vc.stop()
                await self.vc.disconnect()
                self.set_none_song()
                self.vc = None
                self.server_id = None
        
                await self.msg.delete()
                self.msg = None
                
                await interaction.response.defer()

            case "clearq":
                await self.vc.stop()
                await self.vc.resume()
                self.set_none_song()
                self.bot.dispatch("return_message", self.vc.ctx)     
                await interaction.response.defer()

            case "loop":
                if self.loop != 2:
                    self.loop += 1
                else:
                    self.loop = 0
                
                self.bot.dispatch("return_message", self.vc.ctx)
                await interaction.response.defer()

            case "beg":
                await self.vc.seek(position=0)
                await interaction.response.defer()

            case "next":
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

            case "prev":
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
            self.bot.dispatch("return_message", ctx)
            return
        
        if self.loop == 1:
            if self.song_position == len(self.music_queue) - 1:
                self.song_position = 0
            else:
                self.song_position += 1
        
        if self.loop == 0:
            self.song_position += 1
        
        self.bot.dispatch("handle_music", ctx)

    
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
    

    @commands.command(name="clearqueue", aliases=["cq"])
    async def clear(self, ctx, num = None):
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


    # Userlist
    @commands.command(name="printlist", aliases=['ptl'])
    async def load_print(self, ctx, page = 1):
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (ctx.author.id,))
        lst = cursor.fetchall()

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


    @commands.command(name="clearlist", aliases=['cll'])
    async def load_delete(self, ctx, num: int):
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url, id FROM music_data WHERE user_id = %s", (ctx.author.id,))
        lst = cursor.fetchall()

        id = lst[num-1][2]
        name = lst[num-1][0]

        cursor.execute(f'DELETE FROM music_data WHERE id = %s', (id,))
        self.dbconn.commit()
        await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Track **{name}** deleted'))


    @commands.command(name="addtolist", aliases=['atl'])
    async def load_save(self, ctx, *args):
        query = " ".join(args)
        song = await self.get_song(query)

        if song is None:
            await ctx.send(embed=errorEmbedCustom(854, "Not found", "Can't find song"))
            return
        
        title = "[List] " + song[0].name if song[1] else song[0].title
        url = query if song[1] else song[0].uri
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (title, url, ctx.author.id))
        self.dbconn.commit()

        await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{title}**'))

    
    @commands.command(name='playlist', aliases=['pll'])
    async def import_list(self, ctx, num = 0):
        if self.server_id == None:
            self.server_id = ctx.guild.id
        else:
            if self.server_id != ctx.guild.id:
                await ctx.send(embed=errorEmbedCustom(399.1, "VC Error", "Can't execute command. Bot already connected to other guild's channel."))
                return
            
        if ctx.author.voice is None:
            await ctx.send(embed=errorEmbedCustom(399, "VC Error", "Can't get your voice channel"))
            return
        
        voice_channel = ctx.author.voice.channel

        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (ctx.author.id,))
        lst = cursor.fetchall()

        if len(lst) == 0:
            await ctx.send(embed=errorEmbedCustom("804.5", "Can`t read list!", "Error: your list is empty!"))
            return

        if int(num) != 0:
            item = lst[int(num) - 1][1]
            song = await self.get_song(item)

            if song is None:
                await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{lst[int(num) - 1][0]}**"))
                return

            if song[1]:
                for x in song[0].tracks: 
                    self.music_queue.append([x, voice_channel, ctx.author])
            else: self.music_queue.append([song[0], voice_channel, ctx.author])

            if self.vc is None or not self.vc.is_playing():
                self.bot.dispatch("handle_music", ctx)
                return
            
            self.bot.dispatch("return_message", ctx)
            return

        for item in lst:
            song = await self.get_song(item[1])

            if song is None:
                await ctx.send(embed=errorEmbedCustom(854, "Import error", f"Unknown error occurred while importing track **{lst[int(num) - 1][0]}**"))
                continue

            if self.vc is None or not self.vc.is_playing():
                if song[1]:
                    for x in song[0].tracks: 
                        self.music_queue.append([x, voice_channel, ctx.author])
                else: self.music_queue.append([song[0], voice_channel, ctx.author])
                self.bot.dispatch("handle_music", ctx)
            else:
                if song[1]:
                    for x in song[0].tracks: 
                        self.music_queue.append([x, voice_channel, ctx.author])
                else: self.music_queue.append([song[0], voice_channel, ctx.author])

        self.bot.dispatch("return_message", ctx)