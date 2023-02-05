# AT PROJECT Limited 2022 - 2023; ATLB-v1.5.4
import math
import discord
import json
from discord.ext import commands
from embeds import errorEmbedCustom, eventEmbed
from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.song_source = ""
        self.song_title = ""
        self.song_position = 0
        self.loop = 0

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True', 'cookiefile': 'cookies.txt'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

    
        @bot.event
        async def on_display_song(self, ctx):
            await ctx.send(embed=eventEmbed(name="🎵   Now playing", text= f'**{self.song_title}**'))

    def set_none_song(self):
        self.music_queue = []
        self.is_playing = False
        self.song_source = ""
        self.song_title = ""
        self.song_position = 0

    def change_song(self, ctx):
        if len(self.music_queue) > 0:
            if self.song_position == len(self.music_queue) - 1 and self.loop == 0:
                self.set_none_song()
                return
            if self.loop == 0:
                self.song_position += 1
                self.song_source[0] = self.music_queue[self.song_position][0]['source']
                self.song_title = self.music_queue[self.song_position][0]['title']
            elif self.loop == 2:
                if self.song_position == len(self.music_queue) - 1:
                    self.song_position = 0
                else:
                    self.song_position += 1
                self.song_source[0] = self.music_queue[self.song_position][0]['source']
                self.song_title = self.music_queue[self.song_position][0]['title']
            self.play_next(ctx)
        else:
            if self.loop == 1:
                self.play_next(ctx)
            elif self.loop == 2:
                self.play_next(ctx)
            else:
                self.set_none_song()


    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}


    def play_next(self, ctx):
        self.is_playing = True

        m_url = self.song_source[0]

        if not self.loop == 1:
            self.bot.dispatch("display_song", self, ctx)
        self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.change_song(ctx))


    async def play_music(self, ctx):
        self.is_playing = True

        m_url = self.song_source[0]

        if self.vc == None or not self.vc.is_connected():
            self.vc = await self.song_source[1].connect()

            #in case we fail to connect
            if self.vc == None:
                await ctx.send(embed=errorEmbedCustom("872", "Connect error", "Could not connect to the voice channel"))
                return
        else:
            await self.vc.move_to(self.song_source[1])

        self.bot.dispatch("display_song", self, ctx)
        self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.change_song(ctx))


    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *args): 
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(embed=eventEmbed("Connected", "Connected to a voice channel!"))
        elif self.is_paused:
            self.vc.resume()
            self.is_playing = True
            self.is_paused = False
            return
        else:
            song = self.search_yt(query)

            if type(song) == type(True):
                await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
            else:
                if not self.is_playing:
                    self.music_queue.append([song, voice_channel])
                    self.song_source = [song['source'], voice_channel]
                    self.song_title = song['title']
                    await self.play_music(ctx)
                else:
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the queue \n **{song["title"]}**'))
                    self.music_queue.append([song, voice_channel])
    

    @commands.command(name="list", aliases=["q", "lst"])
    async def queue(self, ctx, page = None):
        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(self.music_queue) / 10 + 0.1)
        if page == None:
            page = math.ceil((self.song_position + 1) / 10 + 0.1)
        else:
            page = int(page)

        if page > pages or page < 0: 
            print(page, pages)
            await ctx.send(embed=errorEmbedCustom("801.9", "Incorrect Page", "Requested page is not exist or playlist is empty."))
            return

        if page == 1:
            srt, stp = 0, 9
        else:
            srt = 10 * (page - 1) - 2
            stp = 10 * page - 2

        for i in range(srt, stp):
            if i > len(self.music_queue) - 1:
                break
            if self.song_title == self.music_queue[i][0]['title']:
                retval += "**  • " + self.music_queue[i][0]['title'] + "**\n"
                continue
            retval += "• " + self.music_queue[i][0]['title'] + "\n"
            
        if self.loop == 1:
            embed.add_field(name="📄 Playlist", value=retval)
        elif self.loop == 2:
            embed.add_field(name="📄 Playlist", value=retval)
        else:
            embed.add_field(name="📄 Playlist", value=retval)
        
        if self.loop == 1:
            loop_on = "current song"
        elif self.loop == 2:
            loop_on = "on playlist"
        else:
            loop_on = "turned off"
        footer = f"Page: {page} of {pages}, Loop: {loop_on}"
        embed.set_footer(text=footer)

        await ctx.send(embed = embed)


    @commands.command(name="pause", aliases=["pa"])
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
    

    @commands.command(name="prev", aliases=['pr'])
    async def prev_song(self, ctx):
        if self.song_position != 0:
            self.vc.stop()
            self.song_position -= 2
            self.bot.dispatch("change_song", self, ctx)
        else:
            self.vc.stop()
            self.song_position = len(self.music_queue) - 2
            self.bot.dispatch("change_song", self, ctx)


    @commands.command(name="next", aliases=["n", "s"])
    async def next(self, ctx):
        if self.vc != None and self.vc:
            if self.loop == 2:
                if len(self.music_queue) == 0:
                    self.vc.stop()
                    self.loop = 0
                    self.is_playing = False
                    self.song_source = ""
                    self.song_title = ""
                    self.song_position = 0
                if self.song_position == len(self.music_queue):
                    self.song_position = 0
                self.vc.stop()
                self.bot.dispatch("change_song", self, ctx)
            else:
                self.vc.stop()
                self.bot.dispatch("change_song", self, ctx)

    
    @commands.command(name="disconnect", aliases=["d"])
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()


    @commands.command(name="clearqueue", aliases=["cq"])
    async def clear(self, ctx, num = None):
        if num == None:
            if self.vc != None and self.is_playing:
                self.vc.stop()
            self.set_none_song()
            self.loop = 0
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Queue cleared"))
        else:
            title = self.music_queue[int(num) - 1][0]['title']
            self.music_queue.pop(int(num) - 1)
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Song **" + title + "** succesfully cleared!"))
        
        
    @commands.command(name='loop', aliases=["lp"])
    async def loop(self, ctx):
        match self.loop:
            case 0:
                self.loop += 1
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned on current song."))
            case 1:
                self.loop += 1
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned on playlist."))
            case 2:
                self.loop = 0
                await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned off."))


    # User playlist
    @commands.command(name='playlist', aliases=['pll'])
    async def import_list(self, ctx, num = 0):
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
            song = self.search_yt(item)
            if self.song_source == "":
                self.song_source = [song['source'], voice_channel]
                self.song_title = song['title']
            self.music_queue.append([song, voice_channel])
            if not self.is_playing:
                await self.play_music(ctx)
            return

        for item in list:
            item = item[1]
            song = self.search_yt(item)

            if self.song_source == "":
                self.song_source = [song['source'], voice_channel]
                self.song_title = song['title']
                if not self.is_playing:
                    self.music_queue.append([song, voice_channel])
                    await self.play_music(ctx)
                await ctx.send(embed=eventEmbed(name="🔵 Processing...", text="List import process started, please wait..."))
            else:
                self.music_queue.append([song, voice_channel])
        
        await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Track list succesfully imported!'))


    @commands.command(name="addtolist", aliases=['atl'])
    async def load_save(self, ctx, *args): 
        query = " ".join(args)
        song = self.search_yt(query)

        await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{song["title"]}**'))

        with open('lists.json', 'r+', encoding="utf-8") as f:
            data = json.load(f)
            id = str(ctx.author.id)

            if id in data:
                data[id].append([song['title'], query])
            else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()


    @commands.command(name="printlist", aliases=['ptl'])
    async def load_print(self, ctx): 
        with open('lists.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
            id = str(ctx.author.id)

            if id in data:
                lst = data[id]
                retval = ""
                embed = discord.Embed(color=0x915AF2)

                for i, z in enumerate(lst):
                    z = z[0]
                    if (i > 15): break
                    retval += str(i + 1) + ". " + z + "\n"

                if retval == "": embed.add_field(name="📄 Saved List", value="List is empty.", inline=False)
                else: embed.add_field(name="📄 Saved List", value=retval, inline=False)
                await ctx.send(embed = embed)

            else: await ctx.send(embed=errorEmbedCustom("804", "Uknown list", "Error: you don`t have saved list!"))

    @commands.command(name="clearlist", aliases=['cll'])
    async def load_delete(self, ctx, num = None):
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

    @commands.command(name="initlist", aliases=['inl'])
    async def init_list(self, ctx):
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
    