"""Global constants."""

from __future__ import annotations

from typing import Final

from tcod.event import KeySym

DIRECTION_KEYS: Final = {
    # Arrow keys
    KeySym.LEFT: (-1, 0),
    KeySym.RIGHT: (1, 0),
    KeySym.UP: (0, -1),
    KeySym.DOWN: (0, 1),
    # Arrow key diagonals
    KeySym.HOME: (-1, -1),
    KeySym.END: (-1, 1),
    KeySym.PAGEUP: (1, -1),
    KeySym.PAGEDOWN: (1, 1),
    # Keypad
    KeySym.N4: (-1, 0),
    KeySym.N6: (1, 0),
    KeySym.N8: (0, -1),
    KeySym.N2: (0, 1),
    KeySym.N7: (-1, -1),
    KeySym.N1: (-1, 1),
    KeySym.N9: (1, -1),
    KeySym.N3: (1, 1),
    KeySym.N5: (0, 0),
    # VI keys
    KeySym.h: (-1, 0),
    KeySym.l: (1, 0),
    KeySym.k: (0, -1),
    KeySym.j: (0, 1),
    KeySym.y: (-1, -1),
    KeySym.b: (-1, 1),
    KeySym.u: (1, -1),
    KeySym.n: (1, 1),
    KeySym.PERIOD: (0, 0),
}

INVENTORY_KEYS = "abcdefghijklmnopqrstuvwxyz"
