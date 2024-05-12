from enum import Enum

from wavelink import TrackSource
from discord import VoiceProtocol

class LoopState(Enum):
    STRAIGHT = 0
    LOOP = 1
    CURRENT = 2


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
    def __init__(self, guild: int) -> None:
        self.track_list: list[TrackSource] = list()
        self.voice_client: VoiceProtocol = None
        self.guild: int = guild
        self.position: int = 0
