# AT PROJECT Limited 2022 - 2024; AT_nEXT-v3.6.3
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


class SongSearchResult():
    def __init__(self, song, is_playlist: bool) -> None:
        self.song = song
        self.is_playlist = is_playlist


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
        if not guild in self.players.keys():
            raise PlayerNotFoundException
    
        del self.players[guild]


class music_cog(commands.Cog):
    group = app_commands.Group(name = "list", description = "user list commands group")

    def __init__(self, bot, connection, logger):
        self.controller = ServerController()
        self.bot: commands.Bot = bot
        self.dbconn = connection
        self.logger = logger
        self.msg = {}

    async def is_user_in_voice(self, interaction: discord.Interaction) -> bool:
        if interaction.user.voice is None:
                await interaction.response.send_message(
                    embed=error_embed("870", "VC Error", "Can't get your voice channel"),
                                      ephemeral=True)
                return False

        return True

    async def bot_cleanup(self):
        for message in self.msg:
            if self.msg[message] is not None: await self.msg[message].delete()

    async def play(self, interaction: discord.Interaction, response: SongSearchResult):
        if not await self.is_user_in_voice(interaction):
            return
        
        try:
            interaction_player = self.controller.get_player(interaction.guild_id)
            voice_channel = interaction_player.get_voice_client()
        except PlayerNotFoundException:
            voice_channel = await interaction.user.voice\
                            .channel.connect(cls=wavelink.Player)
            interaction_player = self.controller\
                        .create_player(interaction, voice_channel)

        if response.song is None:
            await interaction.response.send_message(embed=error_embed("872", 
                                "Not found", "Can't find song"), ephemeral = True)
            return
        
        song = response.song

        if response.is_playlist:
                for x in song.tracks: interaction_player.add_song(x, interaction.user.name)
        else: interaction_player.add_song(song, interaction.user.name)
        
        try:
            await interaction.response.send_message("Processing...", ephemeral=True)
        except discord.errors.NotFound:
            interaction.channel.send("Unexpected error, cannot send message.")
            await interaction_player.voice_client.disconnect()
            return

        if voice_channel.playing and interaction_player.get_list_length() != 1:
            self.bot.dispatch("return_message", interaction)
            return
              
        self.bot.dispatch("handle_music", interaction)

    async def nEXT_queue(self, interaction: Interaction):
        interaction_player = self.controller.get_player(interaction.guild_id)

        page = math.ceil((interaction_player.get_position() + 1) / 10 + 0.1)
        pages = math.ceil(interaction_player.get_list_length() / 10 + 0.1)

        view = messages.ListView(
            interaction_player.get_list(),
            interaction_player.get_list_length(),
            pages,
            page,
            True,
            interaction_player.get_position()
        )

        embed = discord.Embed(color=0x915AF2)
        embed.add_field(name="📄 Playlist", value=self.generate_playlist_text(interaction_player, page))
        embed.set_footer(text=f"Page: {page} of {pages}")

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        await view.time_stop()

    def generate_playlist_text(self, interaction_player, page):
        start = 10 * (page - 1) if page > 1 else 0
        end = 10 * page

        playlist_text = []
        for i in range(start, end):
            try:
                track = interaction_player.get_song(i).get_track()
            except ValueError:
                break

            title = self.truncate_title(track.title)

            if i == interaction_player.get_position():
                playlist_text.append(f"**{i + 1}. {title}**")
                continue

            playlist_text.append(f"{i + 1}. {title}")

        return "\n".join(playlist_text)

    def truncate_title(self, title, max_length=65):
        if len(title) > max_length:
            return title[:max_length - 3] + "..."
        return title

    # Listeners
    @commands.Cog.listener()
    async def on_handle_music(self, interaction: discord.Interaction):
        interaction_player = self.controller.get_player(interaction.guild_id)
        voice_client = interaction_player.get_voice_client()

        await voice_client.stop()
        await voice_client.play(interaction_player.get_current_song().get_track())
        
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
        interaction_player = self.controller.get_player(interaction.guild_id)
        track = interaction_player.get_current_song()
        view = ui.View()

        stop_pause_btn = "▶️ Resume" if interaction_player.get_voice_client().paused else "⏸️ Pause"

        loop_state = interaction_player.get_loop_state()
        loop_btn, footer_loop_text = self.get_loop_info(loop_state)

        buttons = [
            ("🔈 Down", "down", 1), ("⏮️ Previous", "prev", 1),
            (stop_pause_btn, "pause", 1), ("⏭️ Next", "next", 1),
            ("🔊 Up", "up", 1), ("📄 Queue", "queue", 2),
            ("🧹 Clear", "clearq", 2), ("⏹️ Stop", "stop", 2),
            (f"{loop_btn[0]} Loop", "loop", 2), ("⏪ Restart", "beg", 2)
        ]

        for label, custom_id, row in buttons:
            style = loop_btn[1] if custom_id == "loop" else ButtonStyle.primary if row == 1 else ButtonStyle.gray
            view.add_item(ui.Button(label=label, style=style, custom_id=custom_id, row=row))

        embed = self.create_embed(track, footer_loop_text, interaction_player)
        await self.send_or_update_message(interaction, embed, view)

    def get_loop_info(self, loop_state):
        loop_info = {
            player.LoopState.STRAIGHT: (["🔁", ButtonStyle.gray], "turned off"),
            player.LoopState.LOOP: (["🔁", ButtonStyle.success], "on playlist"),
            player.LoopState.CURRENT: (["🔂", ButtonStyle.success], "current song")
        }

        return loop_info.get(loop_state, (["🔁", ButtonStyle.gray], "unknown"))

    def create_embed(self, track, loop_on, interaction_player) -> discord.Embed:
        if track:
            song_len = datetime.datetime.fromtimestamp(track.get_track().length / 1000).strftime("%M:%S")
            embed = discord.Embed(
                title=track.get_track().title,
                description=f"Song length: {song_len}\n\n> URL: [link]({track.get_track().uri})\n> Ordered by: `{track.get_user_requested()}`",
                color=0xa31eff
            )

            footer = f"Loop: {loop_on}\nPosition: {interaction_player.get_position() + 1} of {interaction_player.get_list_length()}\nVolume: {interaction_player.get_voice_client().volume}%"
            embed.set_footer(text = footer)
            return embed
        
        embed = discord.Embed(
            title="Music is not playing",
            description="Song length: 00:00\n\n> URL: \n> Ordered by: ",
            color=0xa31eff
        )

        footer = f"Loop: {loop_on}\nPosition: 0 of 0 \nVolume: {interaction_player.get_voice_client().volume}%"
        embed.set_footer(footer)

        return embed

    async def send_or_update_message(self, interaction, embed, view):
        if interaction.guild_id not in self.msg:
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)
            return
        
        try:
            await self.msg[interaction.guild_id].edit(embed=embed, view=view)
        except:
            await self.msg[interaction.guild_id].delete()
            self.msg[interaction.guild_id] = await interaction.channel.send(embed=embed, view=view)

    async def get_song(self, query, type: str = None):
        # Checkin wether query is a soundcloud song
        if type == 'sc':
            if 'sets' in query:
                try:    playlist = await wavelink.SoundCloudPlaylist.search(query)
                except: return SongSearchResult(None, False)
                
                return SongSearchResult(playlist, True)
        
            try:    song = await wavelink.SoundCloudTrack.search(query)
            except: return SongSearchResult(None, False)
            
            if len(song) == 0:
                return SongSearchResult(None, False)
            
            song = song[0]
            return SongSearchResult(song, False)
        
        # Checking whether query is YouTube playlist
        if '&list' in query:
            try:    song = await wavelink.YouTubePlaylist.search(query)
            except: return SongSearchResult(None, False)

            return SongSearchResult(song, True)
        
        # Nah, it isn't. So, it's YouTube video
        try:    song = await wavelink.Playable.search(query)
        except: return SongSearchResult(None, False)

        if len(song) == 0:
            return SongSearchResult(None, False)
        song = song[0]

        return SongSearchResult(song, False)
       
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        payload_player = payload.player
        reason = payload.reason
        interaction_player = self.controller.get_player(payload_player.guild.id)
        interaction = interaction_player.get_interaction()

        if reason == "stopped" and\
                interaction_player.get_list_length() != 0:
            self.bot.dispatch("return_message", interaction)

        if reason == 'finished':
            try:
                interaction_player.next_song()
            except player.EndOfListException:
                interaction_player.clear_list()
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
            interaction_player = self.controller.get_player(interaction.guild.id)
        except PlayerNotFoundException:
            return
        
        voice_client = interaction_player.get_voice_client()

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

            case "stop":
                await voice_client.stop()
                await voice_client.disconnect()
                self.controller.remove_player(interaction.guild_id)

                await self.msg[interaction.guild_id].delete()
                del self.msg[interaction.guild_id]
                
                await interaction.response.defer()

            case "clearq":
                interaction_player.clear_list()

                await voice_client.stop()
                await voice_client.pause(False)

                self.bot.dispatch("return_message", interaction)
                await interaction.response.defer()

            case "loop":
                interaction_player.change_loop_state()      
                self.bot.dispatch("return_message", interaction)
                await interaction.response.defer()

            case "beg":
                await voice_client.seek()
                await interaction.response.defer()

            case "next":
                await interaction.response.defer()

                try:
                    interaction_player.next_song(True)
                except player.EndOfListException:
                    interaction_player.clear_list()
                    self.bot.dispatch("return_message", interaction)
                    return
                
                self.bot.dispatch("handle_music", interaction)
                self.bot.dispatch("return_message", interaction)

            case "prev":
                interaction_player.prev_song()
                await interaction.response.defer()

                self.bot.dispatch("handle_music", interaction)
                self.bot.dispatch("return_message", interaction)
    
    # Commands
    @app_commands.command(name="youtube", description="Play YouTube track")
    @app_commands.describe(query="Song name or link")
    async def play_yt(self, interaction: discord.Interaction, query: str):
        response = await self.get_song(query)
        
        if response.song is None:
            await interaction.response.send_message(embed=error_embed("872", "Not found", "Can't find song"),
                                                    ephemeral=True)
            return

        await self.play(interaction, response.song)

    @app_commands.command(name="soundcloud", description="Play SoundCloud track")
    @app_commands.describe(query="Song name or link")
    async def play_soundcloud(self, interaction: discord.Interaction, query: str):
        response = await self.get_song(query, 'sc')

        if response.song is None:
            await interaction.response.send_message(embed=error_embed("872", "Not found", "Can't find song"),
                                                    ephemeral=True)
            return
        
        await self.play(interaction, response)

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
            interaction_player = self.controller.get_player(interaction.guild_id)
        except PlayerNotFoundException:
            await interaction.response.send_message(embed=error_embed("870.1", "Change error", 
                                                    "Not connected to voice channel."),
                                                    ephemeral = True)
            return

        voice_client = interaction_player.get_voice_client()

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
                text=f"Track **{interaction_player.get_current_song().get_track().title}** seeked for `{txt}`"),
                ephemeral= True)

    @app_commands.command(name="remove", description="Deleting soundtrack from the queue")
    @app_commands.describe(position="Song position")
    async def clear(self, interaction: discord.Interaction, position: int = None):
        interaction_player = self.controller.get_player(interaction.guild_id)
        try:
            if interaction_player.remove_song(position - 1):
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
        songs_list = cursor.fetchall()

        retval = ""
        embed = discord.Embed(color=0x915AF2)

        pages = math.ceil(len(songs_list) / 10 + 0.1)
        page = page if page != 0 else pages

        if page > pages or page <= 0:
            await interaction.followup.send(embed=
                                                    error_embed("873",
                                                    "Incorrect Page", "Requested page is not exist."),
                                                    ephemeral = True)
            return
        
        view = messages.ListView(songs_list, len(songs_list), pages, page)

        if page == 1:
            srt, stp = 0, 10
        else:
            srt = 10 * (page - 1) - 1
            stp = 10 * page - 1
    
        for i in range(srt, stp):
            if i > len(songs_list) - 1:
                break

            if len(songs_list[i][0]) > 65:
                z = len(songs_list[i][0]) - 65
                title = songs_list[i][0][:-z] + "..."
            else:
                title = songs_list[i][0]

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
        songs_list = cursor.fetchall()

        id = songs_list[position - 1][2]
        name = songs_list[position - 1][0]

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
        response = await self.get_song(query, provider.value)

        if response.song is None:
            await interaction.response.send_message(embed=error_embed("872", "Not found", "Can't find song"),
                                                    ephemeral=True)
            return
        
        song = response.song

        title = "[List] " + song.name if response.is_playlist else song.title
        url = query if response.is_playlist else song.uri
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (title, url, interaction.user.id))
        self.dbconn.commit()

        await interaction.response.send_message(embed=event_embed(name="✅ Success!", text= f'Song added to the list \n **{title}**'),
                                                ephemeral=True)
    
    @group.command(name="play", description="Plays songs from user list")
    @app_commands.describe(position="Song numbers. Example: 1, 2, 3 - 5")
    async def user_list_play(self, interaction: discord.Interaction, position: str):
        if not await self.is_user_in_voice(interaction):
            return
        
        try:
            songs = strparser.parse_input(position)
        except strparser.ParseException:
            await interaction.response.send_message(embed=error_embed("876", "Can`t read input!", "Your input is invalid"),
                                                    ephemeral=True)
            return
        
        try:
            interaction_player = self.controller.get_player(interaction.guild_id)
            voice_channel = interaction_player.get_voice_client()
        except PlayerNotFoundException:
            voice_channel = await interaction.user.voice\
                            .channel.connect(cls=wavelink.Player)
            interaction_player = self.controller\
                        .create_player(interaction, voice_channel)

        cursor = self.dbconn.cursor()
        cursor.execute(f"SELECT music_name, music_url FROM music_data WHERE user_id = %s", (interaction.user.id,))
        songs_list = cursor.fetchall()

        if len(songs_list) == 0:
            await interaction.response.send_message(embed=error_embed("873.1", "Can`t read list!", "Error: your list is empty!"),
                                                    ephemeral=True)
            return
            
        error_string = ""
        await interaction.response.send_message("Processing...", ephemeral=True)
        
        for song_id in songs:
            if len(songs_list) - 1 < song_id:
                error_string += f"\n- Song {song_id + 1} not found in list"
                await interaction.edit_original_response(content=f"Error while importing songs: {error_string}")
                continue
            
            response = await self.get_song(songs_list[song_id][1])

            if response is None:
                error_string += f"\n- {songs_list[song_id][0]} [{song_id}]"
                await interaction.edit_original_response(content=f"Error while importing songs: {error_string}")                                                     
                continue

            song = response.song

            if response.is_playlist:
                for x in song.tracks:
                    interaction_player.add_song(x, interaction.user.name)
            else: interaction_player.add_song(song, interaction.user.name)

            if not voice_channel.playing and interaction_player.get_list_length() == 1:
                self.bot.dispatch("handle_music", interaction)
        
        if len(songs) > 1:
            self.bot.dispatch("return_message", interaction)

    @group.command(name="add_current", description="Adds current song to the playlist")
    async def add_current(self, interaction):
        try:
            int_player = self.controller.get_player(interaction.guild_id)

        except PlayerNotFoundException:
            await interaction.response.send_message(embed=error_embed("870", "VC Error", "Can't get your voice channel"),
                                                    ephemeral=True)
            return
        
        song = int_player.get_current_song()

        if song == None:
            await interaction.response.send_message(embed=error_embed("872.3", "Not found", "May be you are not playing any song"),
                                                    ephemeral=True)
            return
        
        song = song.get_track()
        
        cursor = self.dbconn.cursor()
        cursor.execute("INSERT INTO music_data (music_name, music_url, user_id) VALUES (%s, %s, %s)", 
                        (song.title, song.uri, interaction.user.id))
        self.dbconn.commit()

        await interaction.response.send_message(embed=event_embed(name="✅ Success!", 
                                                text=f'Song added to the list \n **{song.title}**'),
                                                ephemeral=True)