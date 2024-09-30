from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Optional, Any


class SequenceGame(Enum):
    OOT = 1
    MM  = 2

# Represents the information associated with a sequence, aside from the sequence data itself
class Sequence:
    def __init__(self, name: str, cosmetic_name: str, seq_type: str, type: int = 0x0202, instrument_set: int | str = 0x03,
                 replaces: int = -1, vanilla_id: int = -1, seq_file: Optional[str] = None, new_instrument_set: bool = False,
                 zsounds: Optional[list[dict[str, str]]] = None) -> None:
        self.name: str = name
        self.seq_file = seq_file
        self.cosmetic_name: str = cosmetic_name
        self.replaces: int = replaces
        self.vanilla_id: int = vanilla_id
        self.seq_type = seq_type
        self.type: int = type
        self.new_instrument_set: bool = new_instrument_set
        self.zsounds: Optional[list[dict[str, str]]] = zsounds
        self.zbank_file: Optional[str] = None
        self.bankmeta: Optional[str] = None
        self.game: Optional[SequenceGame] = SequenceGame.OOT

        self.instrument_set: int = 0x0
        if isinstance(instrument_set, str):
            if instrument_set == '-':
                self.new_instrument_set = True
            else:
                self.instrument_set = int(instrument_set, 16)
        else:
            self.instrument_set = instrument_set

    def copy(self) -> Sequence:
        copy = Sequence(self.name, self.cosmetic_name, self.seq_type, self.type, self.instrument_set, self.replaces, self.vanilla_id, self.seq_file, self.new_instrument_set, self.zsounds)
        copy.zbank_file = self.zbank_file
        copy.bankmeta = self.bankmeta
        copy.game = self.game
        return copy
