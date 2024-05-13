from enum import Enum

from wavelink import TrackSource
from discord import VoiceProtocol

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
    def __init__(self, track: TrackSource,
                 user_requested: str) -> None:
        self.user_requested: str = user_requested
        self.track: TrackSource = track
    
    def get_song(self) -> TrackSource:
        return self.track
    
    def get_user_requested(self) -> str:
        return self.user_requested


class Player():
    def __init__(self, guild: int, voice_client: VoiceProtocol) -> None:
        self.track_list: list[TrackSource] = list()
        self.voice_client: VoiceProtocol = voice_client
        self.guild: int = guild
        self.position: int = 0
        self.loop = LoopState.STRAIGHT

    def next_song(self, change_track: bool) -> TrackSource:
        if len(self.track_list) - 1 == self.position and\
                self.loop == LoopState.STRAIGHT:
            raise EndOfListException
        
        if (not self.loop == LoopState.STRAIGHT or change_track)\
                and self.position == len(self.track_list) - 1:
            self.position = 0
            return
        
        if not self.loop == LoopState.CURRENT or change_track:
            self.position += 1

    def prev_song(self):
        if self.position == 0:
            self.position = len(self.track_list) - 1
        self.position -= 1

    def get_current_song(self):
        return self.track_list[self.position]
    
    def get_song_pos(self, position: int) -> TrackSource:
        if position == len(self.track_list) - 1:
            raise ValueError
        return self.track_list[position]
    
    def get_voice_client(self) -> VoiceProtocol:
        return self.voice_client
    
    def clear_list(self) -> None:
        self.loop = LoopState.STRAIGHT
        self.track_list.clear()
        self.position = 0

    def get_position(self) -> int:
        return self.position
    
    def get_list_length(self) -> int:
        return len(self.track_list)
    
    def get_list(self) -> list[TrackSource]:
        return self.track_list
    
    def get_loop_state(self) -> LoopState:
        return self.loop