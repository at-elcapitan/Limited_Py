from enum import Enum

from wavelink import Playable, Player as WPlayer
from discord import Interaction

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


class Player():
    def __init__(self, interaction: Interaction,
                 voice_client: WPlayer) -> None:
        self.interaction: Interaction = interaction
        self.voice_client: WPlayer = voice_client
        self.track_list: list[Track] = list()
        self.loop = LoopState.STRAIGHT
        self.position: int = 0

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
    
    def get_voice_client(self) -> WPlayer:
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