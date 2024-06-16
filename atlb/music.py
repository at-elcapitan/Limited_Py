# AT PROJECT Limited 2022 - 2024; AT_nEXT-v3.6
import math
import datetime

import discord
import wavelink
from discord import ui
from discord import Interaction
from discord import ButtonStyle
from discord.ext import commands
from discord import app_commands

import player
import messages
import strparser
from embeds import error_embed, event_embed

class PlayerNotFoundException(Exception):
    def __init__(self, player_guild: int):
        super().__init__(f"Player not found with guild {player_guild}")


class ServerController():
    def __init__(self) -> None:
        self.players = {}

    def get_player(self, guild: int) -> player.Player:
        if not guild in self.players.keys():
            raise PlayerNotFoundException(guild)
        
        return self.players[guild]
    
    def create_player(self, interaction: discord.Interaction,
                      voice_channel: discord.VoiceChannel) -> player.Player:
        pl = player.Player(interaction, voice_channel)
        self.players[interaction.guild_id] = pl
        return pl
    
    def remove_player(self, guild) -> None:
        if guild in self.players.keys():
            del self.players[guild]
            return
        raise PlayerNotFoundException


class music_cog(commands.Cog):
    group = app_commands.Group(name = "list", description = "user list commands group")

    def __init__(self, bot, connection, logger):
        self.controller = ServerController()
        self.bot: commands.Bot = bot
        self.dbconn = connection
        self.logger = logger
        self.msg = {}

    async def bot_cleanup(self):
        for message in self.msg:
            if self.msg[message] is not None: await self.msg[message].delete()

    async def play(self, interaction: discord.Interaction, song):
        if interaction.user.voice is None:
            await interaction.response.send_message(embed=error_embed("870",
                        "VC Error", "Can't get your voice channel"), ephemeral = True)
            return
        
        try:
            int_player = self.controller.get_player(interaction.guild_id)
        except PlayerNotFoundException:
            voice_channel = await interaction.user.voice\
                            .channel.connect(cls=wavelink.Player)
            int_player = self.controller\
                        .create_player(interaction, voice_channel)

        if song is None:
            await interaction.response.send_message(embed=error_embed("872", 
                                "Not found", "Can't find song"), ephemeral = True)
            return

        if type(song) == type(True):
            await interaction.response.send_message(embed=error_embed("872.1", "URL Incorrect", 
                "Could not play the song. Incorrect format, try another keyword."
                "This could be due to playlist or a livestream format."), ephemeral = True)
            return
        
        if song[1]:
                for x in song[0].tracks: 
                    int_player.add_song(x, interaction.user.name)
        else: int_player.add_song(song[0], interaction.user.name)
        
        if not int_player.get_voice_client().playing\
                and int_player.get_list_length() == 1:    
            await interaction.response.send_message("Processing...", ephemeral=True)
            self.bot.dispatch("handle_music", interaction)
            return
        
        await interaction.response.send_message("Processing...", ephemeral=True)
        self.bot.dispatch("return_message", interaction)
        
    
    async def nEXT_queue(self, interaction: Interaction):
        int_player = self.controller.get_player(interaction.guild_id)

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        page = math.ceil((int_player.get_position() + 1) / 10 + 0.1)
        pages = math.ceil(int_player.get_list_length() / 10 + 0.1)

        view = messages.ListView(int_player.get_list(), int_player.get_list_length(), 
                                 pages, page, True, int_player.get_position())

        if page == 1:
            srt, stp = 0, 10
        else:
            srt = 10 * (page - 1)
            stp = 10 * page

        for i in range(srt, stp):
            try:
                track = int_player.get_song(i).get_track()
            except ValueError:
                break
            
            if len(track.title) > 65:
                z = len(track.title) - 65
                title = track.title[:-z] + "..."
            else:
                title = track.title

            if i == int_player.get_position():
                retval += f"**{i + 1}. " + title + "\n**"
                continue
            retval += f"{i + 1}. " + title + "\n"
            
        embed.add_field(name="📄 Playlist", value=retval)
        embed.set_footer(text=f"Page: {page} of {pages}")

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        await view.time_stop()

    # Listeners
    @commands.Cog.listener()
    async def on_handle_music(self, interaction: discord.Interaction):
        int_player = self.controller.get_player(interaction.guild_id)
        voice_client = int_player.get_voice_client()

        await voice_client.stop()
        await voice_client.play(int_player.get_current_song().get_track())
        
        self.bot.dispatch("return_message", interaction)

    @commands.Cog.listener()    
    async def on_guilds_autosync(self):
        fmt = await self.bot.tree.sync()
        self.logger.info(f"Synced \x1b[39;1m{len(fmt)}\x1b[39;0m commands [startup sync]")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        fmt = await self.bot.tree.sync()
        self.logger.info(f"Synced {len(fmt)} commands. Initiated by \x1b[39;1m{guild} [{guild.id}]\x1b[39;0m guild"
                         " (on_guild_join)")

    @commands.Cog.listener()
    async def on_return_message(self, interaction: discord.Interaction):
        int_player = self.controller.get_player(interaction.guild_id)
        track = int_player.get_current_song()
        view = ui.View()
    
        if int_player.get_voice_client().paused: clab1 = "▶️ Resume" 
        else: clab1 = "⏸️ Pause"

        match int_player.get_loop_state():
            case player.LoopState.STRAIGHT:
                clab2 = ["🔁", ButtonStyle.gray]
                loop_on = "turned off"
            case player.LoopState.LOOP:
                clab2 = ["🔁", ButtonStyle.success]
                loop_on = "on playlist"
            case player.LoopState.CURRENT:
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

        if track is not None:
            song_len_formatted = datetime.datetime\
                                 .fromtimestamp(track.get_track().length / 1000)\
                                 .strftime("%M:%S")
            
            embed = discord.Embed(title=f"{track.get_track().title}", 
                                  description=f"Song length: {song_len_formatted}\n\n> URL: [link]"
                                    f"({track.get_track().uri})\n> Ordered by:"
                                    f" `{track.get_user_requested()}`", color=0xa31eff,)
            
            footer = f"Loop: {loop_on}\nPosition: {int_player.get_position() + 1} "\
                     f"of {int_player.get_list_length()}\nVolume: {int_player.get_voice_client().volume}%"
        else:
            embed = discord.Embed(title="Music is not playing", 
                                  description=f"Song length: 00:00\n\n> URL: \n> Ordered by: ",
                                  color=0xa31eff)
            footer=f"Loop: {loop_on}\nPosition: 0 of 0 \n"\
                   f"Volume: {int_player.get_voice_client().volume}%"

        embed.set_footer(text=footer)

        if not interaction.guild_id in self.msg.keys():
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)
            return
        
        try:
            await self.msg[interaction.guild_id].edit(embed=embed, view=view)
        except:
            await self.msg[interaction.guild_id].delete()
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)

    async def get_song(self, query, type: str = None):
        playlist = False
        
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
            try:
                song = await wavelink.Playable.search(query)
            except: return None

            if len(song) == 0:
                return None
            song = song[0]

        return [song, playlist]
       
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        payload_player = payload.player
        reason = payload.reason
        int_player = self.controller.get_player(payload_player.guild.id)
        interaction = int_player.get_interaction()

        if reason == "stopped" and\
                int_player.get_list_length() != 0:
            self.bot.dispatch("return_message", interaction)

        if reason == 'finished':
            try:
                int_player.next_song()
            except player.EndOfListException:
                int_player.clear_list()
                self.bot.dispatch("return_message", interaction)
                return
            self.bot.dispatch("handle_music", interaction)
            self.bot.dispatch("return_message", interaction)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: Interaction):
        if interaction.type is not discord.InteractionType.component:
            return

        if interaction.data["component_type"] != 2:
            return
        
        button_id = interaction.data["custom_id"]
        try:
            int_player = self.controller.get_player(interaction.guild.id)
        except PlayerNotFoundException:
            return
        voice_client = int_player.get_voice_client()

        match button_id:
            case "down":
                if not voice_client.volume == 0:
                    await voice_client.set_volume(voice_client.volume - 10)
                    self.bot.dispatch("return_message", interaction)
                    await interaction.response.defer()

            case "up":
                if not voice_client.volume == 150:
                    await voice_client.set_volume(voice_client.volume + 10)
                    self.bot.dispatch("return_message", interaction)
                    await interaction.response.defer()

            case "pause":
                await voice_client.pause(not voice_client.paused)
                self.bot.dispatch("return_message", interaction)
                await interaction.response.defer()


            case "queue":
                await interaction.response.defer()
                await self.nEXT_queue(interaction)
                return

            case "stop":
                await voice_client.stop()
                await voice_client.disconnect()
                self.controller.remove_player(interaction.guild_id)

                await self.msg[interaction.guild_id].delete()
                del self.msg[interaction.guild_id]
                
                await interaction.response.defer()

            case "clearq":
                int_player.clear_list()
                await voice_client.stop()
                await voice_client.pause(False)
                self.bot.dispatch("return_message", interaction)
                await interaction.response.defer()

            case "loop":
                int_player.change_loop_state()      
                self.bot.dispatch("return_message", interaction)
                await interaction.response.defer()

            case "beg":
                await voice_client.seek()
                await interaction.response.defer()

            case "next":
                await interaction.response.defer()
                try:
                    int_player.next_song(True)
                except player.EndOfListException:
                    int_player.clear_list()
                    self.bot.dispatch("return_message", interaction)
                    return
                self.bot.dispatch("handle_music", interaction)
                self.bot.dispatch("return_message", interaction)

            case "prev":
                int_player.prev_song()
                await interaction.response.defer()
                self.bot.dispatch("handle_music", interaction)
                self.bot.dispatch("return_message", interaction)
    
    # Commands
    @app_commands.command(name="youtube", description="Play YouTube track")
    @app_commands.describe(query="Song name or link")
    async def play_yt(self, interaction: discord.Interaction, 
                      query: str):
        if query == '':
            await interaction.response.send_message(embed=error_embed("872.2", "Empty", 
                                                    "Empty request cannot be processed."),
                                                    ephemeral= True)
            return

        song = await self.get_song(query)
        await self.play(interaction, song)

    @app_commands.command(name="soundcloud", description="Play SoundCloud track")
    @app_commands.describe(query="Song name or link")
    async def play_soundcloud(self, 
                      interaction: discord.Interaction, 
                      query: str):
        if query == '':
            await interaction.response.send_message(embed=error_embed("872.2", "Empty", 
                                                    "Empty request cannot be processed."),
                                                    ephemeral= True)
            return

        song = await self.get_song(query, 'sc')
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
        try:
            int_player = self.controller.get_player(interaction.guild_id)
        except PlayerNotFoundException:
            await interaction.response.send_message(embed=error_embed("870.1", "Change error", 
                                                    "Not connected to voice channel."),
                                                    ephemeral = True)
            return

        voice_client = int_player.get_voice_client()

        if voice_client.playing:
            pos = voice_client.position + (seconds * 1000)
            await voice_client.seek(pos)
            
            if seconds > 60:
                m = int(seconds // 60)
                s = int(seconds %  60)

                if s > 9:
                    txt = f'{m}m {s}s'
                else:
                    txt = f'{m}m 0{s}s'

            else:
                txt = f'{int(seconds)}s'

            await interaction.response.send_message(embed=event_embed(name="✅ Seek complete", 
                text=f"Track **{int_player.get_current_song().get_track().title}** seeked for `{txt}`"),
                ephemeral= True)

    @app_commands.command(name="remove", description="Deleting soundtrack from the queue")
    @app_commands.describe(position="Song position")
    async def clear(self, interaction: discord.Interaction, position: int = None):
        int_player = self.controller.get_player(interaction.guild_id)
        try:
            if int_player.remove_song(position - 1):
                self.bot.dispatch("return_message", interaction)
                self.bot.dispatch("handle_music", interaction)
                await interaction.response.send_message("Removed", ephemeral=True)
                return
            self.bot.dispatch("return_message", interaction)
            await interaction.response.send_message("Removed", ephemeral=True)
        except IndexError:
            await interaction.response.send_message(embed = error_embed(
                    "870",
                    "Incorrect position", "Track does not exist."),
                    ephemeral = True
                )
        
    @app_commands.command(name="jmp", description="Jump to a track")
    @app_commands.describe(position="Song position")
    async def song_jump(self, interaction: discord.Interaction, position: int):
        try:
            self.controller.get_player(interaction.guild_id)\
                            .set_position(position - 1)
            await interaction.response.send_message("Processing...", ephemeral=True)
            self.bot.dispatch("handle_music", interaction)
            await interaction.response.defer()
        except:
            await interaction.response.send_message(embed = error_embed(
                    "870",
                    "Incorrect position", "Track does not exist."),
                    ephemeral = True
                )

    # Userlist
    @group.command(name="display", description="Displaying user list")
    @app_commands.describe(page="List page")
    async def user_list_print(self, interaction: discord.Interaction, page: int = 0):
        await interaction.response.defer(ephemeral = True)
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(lst) / 10 + 0.1)
        page = page if page != 0 else pages

        if page > pages or page <= 0:
            await interaction.followup.send(embed=
                                                    error_embed("873",
                                                    "Incorrect Page", "Requested page is not exist."),
                                                    ephemeral = True)
            return
        
        view = messages.ListView(lst, len(lst), pages, page)

        if page == 1:
            srt, stp = 0, 10
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
        embed.set_footer(text=f"Page: {page} of {pages}\n")

        await interaction.followup.send(embed=embed, view=view, ephemeral = True)
        await view.time_stop()

    @group.command(name="remove", description="Removing song by position")
    @app_commands.describe(position="position")
    async def user_list_clear(self, interaction: discord.Interaction, position: int):
        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url, id FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        id = lst[position - 1][2]
        name = lst[position - 1][0]

        cursor.execute(f'DELETE FROM music_data WHERE id = %s', (id,))
        self.dbconn.commit()
        await interaction.response.send_message(embed=event_embed(name="✅ Success!", text= f'Track **{name}** deleted'),
                                                ephemeral=True)

    @group.command(name="add", description="Removing song by position")
    @app_commands.describe(query="Song name or link")
    @app_commands.describe(provider="Song name or link")
    @app_commands.choices(provider=[
        app_commands.Choice(name="YouTube", value='yt'),
        app_commands.Choice(name="SoundCloud", value="sc"),
    ])
    async def user_list_add(self, interaction: discord.Interaction, provider: app_commands.Choice[str], query: str):
        song = await self.get_song(query, provider.value)

        if song is None:
            await interaction.response.send_message(embed=error_embed("872", "Not found", "Can't find song"),
                                                    ephemeral=True)
            return
        
        title = "[List] " + song[0].name if song[1] else song[0].title
        url = query if song[1] else song[0].uri
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (title, url, interaction.user.id))
        self.dbconn.commit()

        await interaction.response.send_message(embed=event_embed(name="✅ Success!", text= f'Song added to the list \n **{title}**'),
                                                ephemeral=True)
    
    @group.command(name="play", description="Plays songs from user list")
    @app_commands.describe(position="Song numbers. Example: 1, 2, 3 - 5")
    async def user_list_play(self, interaction: discord.Interaction, position: str):
        if interaction.user.voice is None:
            await interaction.response.send_message(embed=error_embed("870", "VC Error", "Can't get your voice channel"),
                                                    ephemeral=True)
            return
        
        try:
            songs = strparser.parse_input(position)
        except strparser.ParseException:
            await interaction.response.send_message(embed=error_embed("876", "Can`t read input!", "Your input is invalid"),
                                                    ephemeral=True)
            return
        
        try:
            int_player = self.controller.get_player(interaction.guild_id)
        except PlayerNotFoundException:
            voice_channel = await interaction.user.voice\
                            .channel.connect(cls=wavelink.Player)
            int_player = self.controller\
                        .create_player(interaction, voice_channel)

        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (interaction.user.id,))
        lst = cursor.fetchall()

        if len(lst) == 0:
            await interaction.response.send_message(embed=error_embed("873.1", "Can`t read list!", "Error: your list is empty!"),
                                                    ephemeral=True)
            return
            
        error_string = ""
        await interaction.response.send_message("Processing...", ephemeral=True)
        
        for song_id in songs:
            if len(lst) - 1 < song_id:
                error_string += f"\n- Song {song_id + 1} not found in list"
                await interaction.edit_original_response(content=f"Error while importing songs: {error_string}")
                continue
            
            song = await self.get_song(lst[song_id][1])

            if song is None:
                error_string += f"\n- {lst[song_id][0]} [{song_id}]"
                await interaction.edit_original_response(content=f"Error while importing songs: {error_string}")                                                     
                continue
            if song[1]:
                for x in song[0].tracks: 
                    int_player.add_song(x, interaction.user.name)
            else: int_player.add_song(song[0], interaction.user.name)

            if not voice_channel.playing and int_player.get_list_length() == 1:
                self.bot.dispatch("handle_music", interaction)

        if len(songs) > 1:
            self.bot.dispatch("return_message", interaction)

    @group.command(name="add_current", description="Adds current song to the playlist")
    async def add_current(self, interaction):
        try:
            song: wavelink.GenericTrack = self.song_source[interaction.guild_id][0]
        except:
            await interaction.response.send_message(embed=error_embed("872.3", "Not found", "May be you are not playing any song"),
                                                    ephemeral=True)
            return
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (song.title, song.uri, interaction.user.id))
        self.dbconn.commit()

        await interaction.response.send_message(embed=event_embed(name="✅ Success!", 
                                                text=f'Song added to the list \n **{song.title}**'),
                                                ephemeral=True)