# AT PROJECT Limited 2022 - 2023; ATLB-v1.3.3
from ast import alias
import discord
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
        self.loop = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True', 'cookiefile': 'cookies.txt'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

    
        @bot.event
        async def on_display_song(self, ctx):
            await ctx.send(embed=eventEmbed(name="🎵   Now playing", text= f'**{self.song_title}**'))


    def change_song(self, ctx):
        if len(self.music_queue) > 0:
            if not self.loop:
                self.song_source[0] = self.music_queue[0][0]['source']
                self.song_title = self.music_queue[0][0]['title']
                self.music_queue.pop(0)
            self.play_next(ctx)
        else:
            if self.loop:
                self.play_next(ctx)
            else:
                self.is_playing = False
                self.song_source = ""
                self.song_title = ""


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
                    self.song_source = [song['source'], voice_channel]
                    self.song_title = song['title']
                    await self.play_music(ctx)
                else:
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the queue \n **{song["title"]}**'))
                    self.music_queue.append([song, voice_channel])
    

    @commands.command(name="queue", aliases=["q", "qu"])
    async def queue(self, ctx):
        retval = ""
        for i in range(len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if (i > 4): break
            retval += '- ' + self.music_queue[i][0]['title'] + "\n"

            embed = discord.Embed(color=0x915AF2)

            if self.loop:
                embed.add_field(name="🎵 Now playing", value="- " + self.song_title + " (loop)", inline=False)
            else:
                embed.add_field(name="🎵 Now playing", value="- " + self.song_title, inline=False)
                embed.add_field(name="📄 Queue", value=retval, inline=False)

        if retval != "":
            await ctx.send(embed = embed)
        else:
            if self.song_title == "":
                await ctx.send(embed=eventEmbed(name= "📄 Empty", text = "No music in queue"))
            else:
                embed = discord.Embed(color=0x915AF2)

                if self.loop:
                    embed.add_field(name="🎵 Now playing", value="- " + self.song_title + " (loop)", inline=False)
                else:
                    embed.add_field(name="🎵 Now playing", value="- " + self.song_title, inline=False)
                embed.add_field(name="📄 Empty", value="No music in queue", inline=False)

                await ctx.send(embed = embed)
    

    @commands.command(name="pause")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()


    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            self.loop = False
            self.bot.dispatch("change_song", self, ctx)

    
    @commands.command(name="disconnect", aliases=["d"])
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()


    @commands.command(name="clearqueue", aliases=["cq"])
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()

        self.music_queue = []
        await ctx.send(embed=eventEmbed(text="✅ Success!", name="Queue cleared"))


    @commands.command(name='loop', aliases=["lp"])
    async def loop(self, ctx):
        if not self.loop:
            self.loop = True
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned on current song"))
        else:
            self.loop = False
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned off"))