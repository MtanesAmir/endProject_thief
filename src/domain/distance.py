"""Distance metrics and spatial heuristics."""
import math
from typing import Tuple, Union
from src.domain.grid import GridPos

def manhattan_distance(p1: Union[GridPos, Tuple[int, int]], p2: Union[GridPos, Tuple[int, int]]) -> int:
    t1 = p1.to_tuple() if isinstance(p1, GridPos) else p1
    t2 = p2.to_tuple() if isinstance(p2, GridPos) else p2
    return abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])

def euclidean_distance(p1: Union[GridPos, Tuple[int, int]], p2: Union[GridPos, Tuple[int, int]]) -> float:
    t1 = p1.to_tuple() if isinstance(p1, GridPos) else p1
    t2 = p2.to_tuple() if isinstance(p2, GridPos) else p2
    return math.sqrt((t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2)

def chebyshev_distance(p1: Union[GridPos, Tuple[int, int]], p2: Union[GridPos, Tuple[int, int]]) -> int:
    t1 = p1.to_tuple() if isinstance(p1, GridPos) else p1
    t2 = p2.to_tuple() if isinstance(p2, GridPos) else p2
    return max(abs(t1[0] - t2[0]), abs(t1[1] - t2[1]))
