"""Grid movement and boundary validation logic."""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional, Set, Tuple, Union

@dataclass(frozen=True)
class GridPos:
    row: int
    col: int

    def to_tuple(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def is_valid(self, grid_size: int = 7) -> bool:
        return 0 <= self.row < grid_size and 0 <= self.col < grid_size


class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    STAY = (0, 0)
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    WEST = (0, -1)
    EAST = (0, 1)


def legal_moves(
    pos: Union[GridPos, Tuple[int, int]],
    grid_size: int = 7,
    barriers: Optional[Iterable[Union[GridPos, Tuple[int, int]]]] = None,
) -> List[GridPos]:
    if isinstance(pos, tuple):
        pos = GridPos(pos[0], pos[1])

    barrier_set: Set[Tuple[int, int]] = set()
    if barriers:
        for b in barriers:
            barrier_set.add(b.to_tuple() if isinstance(b, GridPos) else b)

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    valid = []
    for dr, dc in deltas:
        nr, nc = pos.row + dr, pos.col + dc
        if 0 <= nr < grid_size and 0 <= nc < grid_size and (nr, nc) not in barrier_set:
            valid.append(GridPos(nr, nc))
    return valid


class MovementEngine:
    def __init__(self, initial_pos: Union[GridPos, Tuple[int, int]] = (3, 3), grid_size: int = 7):
        self.pos = GridPos(*initial_pos) if isinstance(initial_pos, tuple) else initial_pos
        self.grid_size = grid_size

    def get_position(self) -> GridPos:
        return self.pos

    def preview_move(self, direction: Union[Direction, Tuple[int, int]]) -> GridPos:
        d = direction.value if isinstance(direction, Direction) else direction
        return GridPos(self.pos.row + d[0], self.pos.col + d[1])

    def get_legal_moves(self, barriers: Optional[Iterable[Union[GridPos, Tuple[int, int]]]] = None) -> List[GridPos]:
        return legal_moves(self.pos, self.grid_size, barriers)

    def move(self, direction: Union[Direction, Tuple[int, int]], barriers: Optional[Iterable[Union[GridPos, Tuple[int, int]]]] = None) -> bool:
        target = self.preview_move(direction)
        if target in self.get_legal_moves(barriers):
            self.pos = target
            return True
        return False
