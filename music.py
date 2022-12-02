from ast import alias
import nextcord as discord
from nextcord.ext import commands
from embeds import errorEmbedCustom, eventEmbed
import youtube_dl as ydl
from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False
        self.now_playing = ""
        self.loop = False

        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            self.now_playing = self.music_queue[0][0]['title']

            if not self.loop:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
                self.music_queue.pop(0)
            else:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.now_playing = ""
            self.is_playing = False

    # infinite loop checking
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send(embed=errorEmbedCustom("872", "Connect error", "Could not connect to the voice channel"))
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.now_playing = self.music_queue[0][0]['title']

            if not self.loop:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
                self.music_queue.pop(0)
            else:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.now_playing = ""
            self.is_playing = False

    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send(embed=eventEmbed("Connected", "Connected to a voice channel!"))
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(embed=errorEmbedCustom("801", "URL Incorrect", "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."))
            else:
                self.music_queue.append([song, voice_channel])

                if not self.is_playing:
                    await ctx.send(embed=eventEmbed(name="🎵   Now playing", text= f'**{song["title"]}**'))
                    await self.play_music(ctx)
                else:
                    await ctx.send(embed=eventEmbed(name="✅ Success!", text= f'Song added to the queue \n **{song["title"]}**'))

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx)

            if self.loop:
                self.music_queue.pop(0)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(len(self.music_queue)):
            # display a max of 5 songs in the current queue
            if (i > 4): break
            retval += '- ' + self.music_queue[i][0]['title'] + "\n"
            now_pl = self.now_playing

            embed = discord.Embed(color=0x915AF2)

            if self.loop:
                embed.add_field(name="🎵 Now playing", value="- " + self.now_playing + " (loop)", inline=False)
            else:
                embed.add_field(name="🎵 Now playing", value="- " + self.now_playing, inline=False)
                embed.add_field(name="📄 Queue", value=retval, inline=False)

        if retval != "":
            await ctx.send(embed = embed)
        else:
            if self.now_playing == "":
                await ctx.send(embed=eventEmbed(name= "📄 Empty", text = "No music in queue"))
            else:
                embed = discord.Embed(color=0x915AF2)

                if self.loop:
                    embed.add_field(name="🎵 Now playing", value="- " + self.now_playing + " (loop)", inline=False)
                else:
                    embed.add_field(name="🎵 Now playing", value="- " + self.now_playing, inline=False)
                embed.add_field(name="📄 Empty", value="No music in queue", inline=False)

                await ctx.send(embed = embed)

    @commands.command(name="clearqueue", aliases=["cq", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()

        self.music_queue = []
        await ctx.send(embed=eventEmbed(text="✅ Success!", name="Queue cleared"))

    @commands.command(name="disconnect", aliases=["d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

    @commands.command(name='loop', aliases=["lp"], help="Loops current song")
    async def loop(self, ctx):
        if not self.loop:
            self.loop = True
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned on current song"))
        else:
            self.loop = False
            await ctx.send(embed=eventEmbed(name="✅ Success!", text="Loop turned off"))
