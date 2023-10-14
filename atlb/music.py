# AT PROJECT Limited 2022 - 2023; ATLB-v3.1
import math
import asyncio
import datetime

import discord
import wavelink
from wavelink.ext import spotify
import messages
from discord import ui
from discord import Interaction
from discord import ButtonStyle
from discord.ext import commands
from discord import app_commands
from embeds import errorEmbedCustom, eventEmbed

class music_cog(commands.Cog):
    def __init__(self, bot, connection, guilds, logger):
        self.logger = logger
        self.bot: commands.Bot = bot
        self.dbconn = connection
        self.vc = {}
        self.music_queue = {}
        self.song_source = {}
        self.song_title = {}
        self.song_position = {}
        self.loop = {}
        self.msg = {}

        for guild in guilds:
            self.vc[guild] = None
            self.music_queue[guild] = []
            self.song_source[guild] = None
            self.song_title[guild] = None
            self.song_position[guild] = 0
            self.loop[guild] = False
            self.msg[guild] = None

        self.bot.tree.add_command(self.play_yt)
        self.bot.tree.add_command(self.play_soundcloud)
        self.bot.tree.add_command(self.play_spotify)
        self.bot.tree.add_command(self.user_list_clear)
        self.bot.tree.add_command(self.user_list_print)
        self.bot.tree.add_command(self.load_save)
        self.bot.tree.add_command(self.import_list)
        self.bot.tree.add_command(self.music_seek)
        self.bot.tree.add_command(self.resend_song_ctl)
        self.bot.tree.add_command(self.clear)


    
    async def play(self, interaction: discord.Interaction, song):
        if song is None:
            await interaction.response.send_message(embed=errorEmbedCustom(854, "Not found", "Can't find song"), ephemeral = True)
            return
        
        if interaction.user.voice is None:
            await interaction.response.send_message(embed=errorEmbedCustom(399, "VC Error", "Can't get your voice channel"), ephemeral = True)
            return

        voice_channel = interaction.user.voice.channel

        if type(song) == type(True):
            await interaction.response.send_message(embed=errorEmbedCustom("801", "URL Incorrect", 
                "Could not play the song. Incorrect format, try another keyword. This could be due to playlist or a livestream format."), ephemeral = True)
            return
        
        if song[1]:
                for x in song[0].tracks: 
                    self.music_queue[interaction.guild_id].append([x, voice_channel, interaction.user])
        else: self.music_queue[interaction.guild_id].append([song[0], voice_channel, interaction.user])
        
        if self.vc[interaction.guild_id] is None or not self.vc[interaction.guild_id].is_playing() and len(self.music_queue[interaction.guild_id]) == 1:    
            self.bot.dispatch("handle_music", interaction)
            return

        self.bot.dispatch("return_message", interaction)


    def set_none_song(self, interaction: discord.Interaction):
        self.music_queue[interaction.guild_id] = []
        self.song_source[interaction.guild_id] = []
        self.song_title[interaction.guild_id] = ""
        self.loop[interaction.guild_id] = 0
        self.song_position[interaction.guild_id] = 0


    def change_song(self, interaction: discord.Interaction):
        if self.song_position[interaction.guild_id] == len(self.music_queue[interaction.guild_id]) - 1 and self.loop[interaction.guild_id] == 0:
            self.set_none_song(interaction.guild_id)
            self.bot.dispatch("return_message", interaction.guild_id)
            return
        
        if self.loop[interaction.guild_id] == 1:
            if self.song_position[interaction.guild_id] == len(self.music_queue[interaction.guild_id]) - 1:
                self.song_position[interaction.guild_id] = 0
            else:
                self.song_position[interaction.guild_id] += 1
        
        if self.loop[interaction.guild_id] == 0:
            self.song_position[interaction.guild_id] += 1
        
        self.bot.dispatch("handle_music", interaction.guild_id)

    
    async def nEXT_queue(self, interaction: Interaction):
        guildid = interaction.guild.id
        view = messages.ListControl(self.music_queue[guildid], self.song_position[guildid])

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(self.music_queue[guildid]) / 10 + 0.1)
        srt, stp = 0, 9

        for i in range(srt, stp):
            if i > len(self.music_queue[guildid]) - 1:
                break
            if len(self.music_queue[guildid][i][0].title) > 65:
                z = len(self.music_queue[guildid][i][0].title) - 65
                title = self.music_queue[guildid][i][0].title[:-z] + "..."
            else:
                title = self.music_queue[guildid][i][0].title

            if i == self.song_position[guildid]:
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


    # Listeners
    @commands.Cog.listener()
    async def on_handle_music(self, interaction: discord.Interaction):
        self.song_source[interaction.guild_id] = self.music_queue[interaction.guild_id][self.song_position[interaction.guild_id]]
        self.song_title[interaction.guild_id] = self.song_source[interaction.guild_id][0].title

        if self.vc[interaction.guild_id] is None:
            self.vc[interaction.guild_id]: wavelink.Player = await self.song_source[interaction.guild_id][1].connect(cls=wavelink.Player)
            self.vc[interaction.guild_id].interaction = interaction

        await self.vc[interaction.guild_id].play(self.song_source[interaction.guild_id][0])
        self.bot.dispatch("return_message", interaction)


    @commands.Cog.listener()
    async def on_guilds_autosync(self, guilds):
        for guild in guilds:
            fmt = await self.bot.tree.sync(guild=guild)
            self.logger.info(f"Synced {len(fmt)} commands for \x1b[39;1m{guild} [{guild.id}]\x1b[39;0m guild")


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        fmt = await self.bot.tree.sync(guild=guild)
        self.logger.info(f"Synced {len(fmt)} commands for \x1b[39;1m{guild} [{guild.id}]\x1b[39;0m guild")


    @commands.Cog.listener()
    async def on_return_message(self, interaction: discord.Interaction):
        view = ui.View()

        if self.vc[interaction.guild_id].is_paused(): clab1 = "▶️ Resume" 
        else: clab1 = "⏸️ Pause"

        match self.loop[interaction.guild_id]:
            case 0:
                clab2 = ["🔁", ButtonStyle.gray]
                loop_on = "turned off"
            case 1:
                clab2 = ["🔁", ButtonStyle.success]
                loop_on = "on playlist"
            case 2:
                clab2 = ["🔂", ButtonStyle.success]
                loop_on = "current song"

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

        if len(self.music_queue[interaction.guild_id]) != 0:
            song_len_formatted = datetime.datetime.fromtimestamp(self.song_source[interaction.guild_id][0].length / 1000).strftime("%M:%S")
            embed = discord.Embed(title=f"{self.song_title[interaction.guild_id]}", description=f"Song length: {song_len_formatted}\n\n> URL: [link]({self.song_source[interaction.guild_id][0].uri})\n> Ordered by: `{self.song_source[interaction.guild_id][2]}`", color=0xa31eff)        
        else:
            embed = discord.Embed(title="Music is not playing", description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ", color=0xa31eff)


        footer = f"Loop: {loop_on}\nPosition: {self.song_position[interaction.guild_id] + 1} of {len(self.music_queue[interaction.guild_id])}\nVolume: {self.vc[interaction.guild_id].volume}%"
        embed.set_footer(text=footer)

        if self.msg[interaction.guild_id] == None:
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)
            return
        
        try:
            await self.msg[interaction.guild_id].edit(embed=embed, view=view)
        except discord.errors.HTTPException:
            await self.msg[interaction.guild_id].delete()
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)


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
        

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        reason = payload.reason

        if reason == "STOPPED" and not self.vc[player.guild.id] == None and len(self.music_queue[player.guild.id]) != 0:
            self.bot.dispatch("return_message", player.interaction)

        try:
            if reason == 'FINISHED':    
                self.change_song(player.interaction)
        except:
            pass


    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        if interaction.type is not discord.InteractionType.component:
            return

        guildid = interaction.guild.id
        if interaction.data["component_type"] != 2:
            return
        
        button_id = interaction.data["custom_id"]

        match button_id:
            case "down":
                if not self.vc[guildid].volume == 0:
                    await self.vc[guildid].set_volume(self.vc[guildid].volume - 10)
                    self.bot.dispatch("return_message", self.vc[guildid].interaction)
                    await interaction.response.defer()

            case "up":
                if not self.vc[guildid].volume == 150:
                    await self.vc[guildid].set_volume(self.vc[guildid].volume + 10)
                    self.bot.dispatch("return_message", self.vc[guildid].interaction)
                    await interaction.response.defer()

            case "pause":
                if not self.vc[guildid].is_paused():
                    await self.vc[guildid].pause()

                    self.bot.dispatch("return_message", self.vc[guildid].interaction)
                    await interaction.response.defer()
                    return

                await self.vc[guildid].resume()
                self.bot.dispatch("return_message", self.vc[guildid].interaction)
                await interaction.response.defer()


            case "queue":
                await self.nEXT_queue(interaction)

            case "stop":
                await self.vc[guildid].stop()
                await self.vc[guildid].disconnect()
                self.set_none_song(self.vc[guildid].interaction)
                self.vc[guildid] = None
        
                await self.msg[guildid].delete()
                self.msg[guildid] = None
                
                await interaction.response.defer()

            case "clearq":
                await self.vc[guildid].stop()
                await self.vc[guildid].resume()
                self.set_none_song(self.vc[guildid].interaction)
                self.bot.dispatch("return_message", self.vc[guildid].interaction)     
                await interaction.response.defer()

            case "loop":
                if self.loop[guildid] != 2:
                    self.loop[guildid] += 1
                else:
                    self.loop[guildid] = 0
                
                self.bot.dispatch("return_message", self.vc[guildid].interaction)
                await interaction.response.defer()

            case "beg":
                await self.vc[guildid].seek(position=0)
                await interaction.response.defer()

            case "next":
                if self.vc[guildid] != None:
                    if self.loop[guildid] == 1:
                        if len(self.music_queue[guildid]) == 0:
                            await self.vc[guildid].stop()
                            self.set_none_song(self.vc[guildid].interaction)

                        if self.song_position[guildid] == len(self.music_queue[guildid]):
                            self.song_position[guildid] = 0

                        await self.vc[guildid].stop()
                        self.change_song(self.vc[guildid].interaction)
                        await interaction.response.defer()
                        return
                    
                    await self.vc[guildid].stop()
                    if self.loop[guildid] == 2:
                        self.song_position[guildid] += 1

                    self.change_song(self.vc[guildid].interaction)

                self.bot.dispatch("return_message", self.vc[guildid].interaction)
                await interaction.response.defer()

            case "prev":
                if self.song_position[guildid] != 0:
                    await self.vc[guildid].stop()
                    if self.loop[guildid] == 2: self.song_position[guildid] -= 1
                    else: self.song_position[guildid] -= 2
                    self.change_song(self.vc[guildid].interaction)
                else:
                    await self.vc[guildid].stop()
                    if self.loop[guildid] == 2: self.song_position[guildid] = len(self.music_queue[guildid]) - 1
                    else: self.song_position[guildid] = len(self.music_queue[guildid]) - 2
                    self.change_song(self.vc[guildid].interaction)

                self.bot.dispatch("return_message", self.vc[guildid].interaction)
                await interaction.response.defer()
    

    # Commands
    @app_commands.command(name="youtube", description="Play YouTube track")
    @app_commands.describe(query="Song name or link")
    async def play_yt(self, 
                      interaction: discord.Interaction, 
                      query: str):

        if query == '':
            await interaction.response.send_message(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."),
                                                    ephemeral= True)
            return

        await interaction.response.send_message("Processing...", ephemeral=True)
        song = await self.get_song(query)
        await self.play(interaction, song)


    @app_commands.command(name="soundcloud", description="Play SoundCloud track")
    @app_commands.describe(query="Song name or link")
    async def play_soundcloud(self, 
                      interaction: discord.Interaction, 
                      query: str):
        if query == '':
            await interaction.response.send_message(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."),
                                                    ephemeral= True)
            return

        song = await self.get_song(query, 'sc')
        await interaction.response.send_message("Processing...", ephemeral=True)
        await self.play(interaction, song)


    @app_commands.command(name="spotify", description="Play Spotify track")
    @app_commands.describe(query="Song name or link")
    async def play_spotify(self, 
                      interaction: discord.Interaction, 
                      query: str):
        if query == '':
            await interaction.response.send_message(embed=errorEmbedCustom(854, "Empty", "Empty request cannot be processed."),
                                                    ephemeral= True)
            return

        song = await self.get_song(query, 's')
        await interaction.response.send_message("Processing...", ephemeral=True)
        await self.play(interaction, song)


    @app_commands.command(name="resend_control", description="Resends music control panel")
    async def resend_song_ctl(self, interaction: discord.Interaction):
        await self.msg[interaction.guild_id].delete()
        self.msg[interaction.guild_id] = None
        await interaction.response.send_message("Processing...", ephemeral=True)
        self.bot.dispatch("return_message", interaction)


    @app_commands.command(name="seek", description="Seeks current soundtrack")
    @app_commands.describe(seconds="Seconds to seek")
    async def music_seek(self, interaction: discord.Interaction, seconds: int):
        if self.vc[interaction.guild_id] == None:
            await interaction.response.send_message(embed=errorEmbedCustom("872", "Change error", "Not connected to voice channel."),
                                                    ephemeral = True)
            return


        if self.vc[interaction.guild_id].is_playing():
            pos = self.vc[interaction.guild_id].position + (seconds * 1000)
            await self.vc[interaction.guild_id].seek(position=pos)
            
            if seconds > 60:
                m = int(seconds // 60)
                s = int(seconds %  60)

                if s > 9:
                    txt = f'{m}m {s}s'
                else:
                    txt = f'{m}m 0{s}s'

            else:
                txt = f'{int(seconds)}s'
                await interaction.response.send_message(embed=eventEmbed(name="✅ Seek complete", 
                                                                         ext=f"Track **{self.song_title}** seeked for `{txt}`"),
                                                        ephemeral= True)


    @app_commands.command(name="clear", description="Deleting soundtrack from the queue")
    @app_commands.describe(position="Song position")
    async def clear(self, interaction: discord.Interaction, position: int = None):
        title = self.music_queue[interaction.guild_id][int(position) - 1][0].title

        if title == self.song_title[interaction.guild_id]:
            await self.vc[interaction.guild_id].stop()
            self.change_song(interaction)

        await interaction.response.send_message("Processing...", ephemeral=True)
        self.bot.dispatch("return_message", interaction)
        

    # Userlist
    @app_commands.command(name="list_show", description="Displaying user list")
    @app_commands.describe(page="List page")
    async def user_list_print(self, interaction: discord.Interaction, page: int = 1):
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(lst) / 10 + 0.1)
        page = int(page)

        if page > pages or page <= 0:
            await interaction.response.send_message(embed=
                                                    errorEmbedCustom("801.7",
                                                    "Incorrect Page", "Requested page is not exist."),
                                                    ephemeral = True)
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
        await interaction.response.send_message(embed=embed, ephemeral = True)


    @app_commands.command(name="list_clear", description="Removing song by position")
    @app_commands.describe(position="position")
    async def user_list_clear(self, interaction: discord.Interaction, position: int):
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url, id FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        id = lst[position - 1][2]
        name = lst[position - 1][0]

        cursor.execute(f'DELETE FROM music_data WHERE id = %s', (id,))
        self.dbconn.commit()
        await interaction.response.send_message(embed=eventEmbed(name="✅ Success!", text= f'Track **{name}** deleted'),
                                                ephemeral=True)


    @app_commands.command(name="list_add", description="Removing song by position")
    @app_commands.describe(query="Song name or link")
    @app_commands.describe(provider="Song name or link")
    @app_commands.choices(provider=[
        app_commands.Choice(name="YouTube", value='yt'),
        app_commands.Choice(name="SoundCloud", value="sc"),
        app_commands.Choice(name="Spotify", value="s"),
    ])
    async def load_save(self, interaction: discord.Interaction, query: str, provider: app_commands.Choice[str]):
        song = await self.get_song(query, provider.value)

        if song is None:
            await interaction.response.send_message(embed=errorEmbedCustom(854, "Not found", "Can't find song"),
                                                    ephemeral=True)
            return
        
        title = "[List] " + song[0].name if song[1] else song[0].title
        url = query if song[1] else song[0].uri
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (title, url, interaction.user.id))
        self.dbconn.commit()

        await interaction.response.send_message(embed=eventEmbed(name="✅ Success!", text= f'Song added to the list \n **{title}**'),
                                                ephemeral=True)

    
    @app_commands.command(name="list_play", description="Plays songs from user list")
    @app_commands.describe(position="Song position [optional]")
    async def import_list(self, interaction: discord.Interaction, position: int = 0):
        if interaction.user.voice is None:
            await interaction.response.send_message(embed=errorEmbedCustom(399, "VC Error", "Can't get your voice channel"),
                                                    ephemeral=True)
            return
        
        voice_channel = interaction.user.voice.channel

        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        if len(lst) == 0:
            await interaction.response.send_message(embed=errorEmbedCustom("804.5", "Can`t read list!", "Error: your list is empty!"),
                                                    ephemeral=True)
            return

        if int(position) != 0:
            item = lst[int(position) - 1][1]
            song = await self.get_song(item)

            if song is None:
                await interaction.response.send_message(embed=errorEmbedCustom(854, "Import error", 
                                                                               f"Unknown error occurred while importing track **{lst[int(position) - 1][0]}**"),
                                                                               ephemeral=True)
                return

            if song[1]:
                for x in song[0].tracks: 
                    self.music_queue[interaction.guild_id].append([x, voice_channel, interaction.user])
            else: self.music_queue[interaction.guild_id].append([song[0], voice_channel, interaction.user])

            if self.vc[interaction.guild_id] is None or not self.vc[interaction.guild_id].is_playing() and len(self.music_queue[interaction.guild_id]) == 1:
                self.bot.dispatch("handle_music", interaction)
                return
            
            self.bot.dispatch("return_message", interaction)
            return

        for item in lst:
            song = await self.get_song(item[1])

            if song is None:
                await interaction.response.send_message(embed=errorEmbedCustom(854, "Import error",
                                                                                f"Unknown error occurred while importing track **{lst[int(position) - 1][0]}**"),
                                                                                ephemeral=True)
                continue

            if song[1]:
                for x in song[0].tracks: 
                    self.music_queue[interaction.guild_id].append([x, voice_channel, interaction.user])
            else: self.music_queue[interaction.guild_id].append([song[0], voice_channel, interaction.user])

            if self.vc[interaction.guild_id] is None or not self.vc[interaction.guild_id].is_playing() and len(self.music_queue[interaction.guild_id]) == 1:
                self.bot.dispatch("handle_music", interaction)
                continue
        
        await interaction.response.send_message("Processing...", ephemeral=True)
        self.bot.dispatch("return_message", interaction)