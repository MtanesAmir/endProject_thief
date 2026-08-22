"""Distance metrics and spatial heuristics."""
import math
from typing import Tuple, Union
from src.domain.grid import GridPos, legal_moves
from collections import deque

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

def bfs_distance(p1: Union[GridPos, Tuple[int, int]], p2: Union[GridPos, Tuple[int, int]], grid_size: int = 7, barriers: list = None) -> int:
    t1 = p1.to_tuple() if isinstance(p1, GridPos) else p1
    t2 = p2.to_tuple() if isinstance(p2, GridPos) else p2
    
    if t1 == t2:
        return 0
        
    queue = deque([(t1, 0)])
    visited = {t1}
    
    while queue:
        current_pos, dist = queue.popleft()
        
        if current_pos == t2:
            return dist
            
        # Get legal neighbors (exclude STAY which is the first delta usually, but legal_moves handles barriers)
        neighbors = [p.to_tuple() for p in legal_moves(current_pos, grid_size=grid_size, barriers=barriers) if p.to_tuple() != current_pos]
        
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
                
    return 999  # Unreachable
