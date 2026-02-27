# AT PROJECT Limited 2022 - 2024; nEXT-v4.0_beta.2
from enum import Enum

import discord
from discord import Interaction, Message
from wavelink import Playable, Player

from logger import logger

class LoopState(Enum):
    STRAIGHT = 0
    LOOP = 1
    CURRENT = 2


class EndOfListException(Exception):
    def __init__(self) -> None:
        super().__init__("End of list reached")


class NoneVoiceClientException(Exception):
    def __init__(self) -> None:
        super().__init__("Voice client is None")


class Track():
    def __init__(self, track: Playable,
                 user_requested: str) -> None:
        self.user_requested: str = user_requested
        self.track: Playable = track
    
    def get_track(self) -> Playable:
        return self.track
    
    def get_user_requested(self) -> str:
        return self.user_requested


class InteractionPlayer():
    def __init__(self, interaction: Interaction,
                 voice_client: Player) -> None:
        self.interaction: Interaction = interaction
        self.voice_client: Player = voice_client
        self.track_list: list[Track] = list()
        self.loop = LoopState.STRAIGHT
        self.position: int = 0
        self.msg: Message = None

    def next_song(self, change_track: bool = False) -> None:
        if len(self.track_list) - 1 == self.position and\
                self.loop == LoopState.STRAIGHT:
            raise EndOfListException
        
        if (not self.loop == LoopState.STRAIGHT or change_track)\
                and self.position == len(self.track_list) - 1:
            self.position = 0
            return
        
        if not self.loop == LoopState.CURRENT or change_track:
            self.position += 1

    def prev_song(self) -> None:
        if self.position == 0:
            self.position = len(self.track_list) - 1
            return
        
        self.position -= 1

    def get_current_song(self) -> Track:
        if len(self.track_list) == 0:
            return None
        
        return self.track_list[self.position]
    
    def get_song(self, position: int) -> Track:
        if position > len(self.track_list) - 1:
            raise ValueError
        
        return self.track_list[position]
    
    def get_voice_client(self) -> Player:
        return self.voice_client
        
    def clear_list(self) -> None:
        self.loop = LoopState.STRAIGHT
        self.track_list.clear()
        self.position = 0

    def get_position(self) -> int:
        return self.position
    
    def get_list_length(self) -> int:
        return len(self.track_list)
    
    def get_list(self) -> list[Track]:
        return self.track_list
    
    def get_loop_state(self) -> LoopState:
        return self.loop
    
    def set_position(self, position: int) -> None:
        """Sets new position. Raises IndexError"""
        if position > len(self.track_list) - 1:
            raise IndexError
        
        self.position = position
    
    def change_loop_state(self) -> None:
        if self.loop == LoopState.CURRENT:
            self.loop = LoopState.STRAIGHT
            return
        
        if self.loop == LoopState.LOOP:
            self.loop = LoopState.CURRENT
            return
        
        self.loop = LoopState.LOOP
        
    def add_song(self, song: Playable, user: str) -> None:
        track = Track(song, user)
        self.track_list.append(track)

    def get_interaction(self):
        return self.interaction
    
    def remove_song(self, position: int) -> bool:
        """Returns true if you need to change track after removing (current track was removed)
        
        Raises IndexError
        """
        if position > len(self.track_list):
            raise IndexError
        
        if len(self.track_list) == 1:
            self.clear_list()
            return False
        
        if position == self.position:
            if self.position == len(self.track_list) - 1:
                self.position -= 1
            self.track_list.pop(position)
            return True
        
        self.track_list.pop(position)
        return False    

    def get_msg(self) -> Message | None:
        return self.msg
    
    async def delete_message(self):
        """Raises discord.HTTPException to be handled at parrent method"""
        try:
            await self.msg.delete()
        except discord.NotFound:
            return
        except discord.Forbidden as e:
            logger.warning(
                f"Unable to delete message, forbidden. {e}"
            )
        except discord.HTTPException as e:
            logger.error(f"Unexpected HTTP exception. {e}")
            raise discord.HTTPException

        self.msg = None

    async def send_message(self,
                           embed: discord.Embed,
                           view: discord.ui.View,
                           interaction: discord.Interaction):
        """Raises: discord.HTTPException from interaction.channel.send"""
        try:
            self.msg = await interaction.channel.send(embed=embed, view=view)
        except discord.NotFound as e:
            logger.warning(e)
        except discord.Forbidden as e:
            logger.warning(
                f"Unable to delete message, forbidden. {e}"
            )
        except discord.HTTPException as e:
            logger.error(f"Unexpected HTTP exception. {e}")
            raise discord.HTTPException


    async def edit_message(self,
                           view: discord.ui.View, 
                           embed: discord.Embed):
        """Raises: discord.HTTPException, discord.NotFound (if self.msg is None)

        Not handles: discord.NotFound from discord.Message.edit (to be handled in parrent function)
        """
        if self.msg is None:
            raise discord.NotFound

        try:
            await self.msg.edit(view=view, embed=embed)
        except discord.Forbidden as e:
            logger.warning(
                f"Unable to delete message, forbidden. {e}"
            )
        except discord.HTTPException as e:
            logger.error(f"Unexpected HTTP exception. {e}")
            raise discord.HTTPException