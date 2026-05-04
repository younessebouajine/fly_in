# 1. Start at start_zone, cost = 0
# 2. Keep a priority queue → always pick the zone with LOWEST cost
# 3. For each neighbor:
#    - new_cost = current_cost + move_cost(neighbor)
#    - if new_cost < known_cost → update and add to queue
# 4. Skip blocked zones
# 5. Stop when you reach end_zone
# 6. Reconstruct path using "came_from" dict

import heapq
from typing import List, Optional
from models import Zone, MapData

class PathFinder:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data

    def get_move_cost(self, zone: Zone) -> int:
        """Return movement cost based on zone type"""
        ...

    def find_path(self, start: Zone, end: Zone) -> Optional[List[Zone]]:
        """Dijkstra — returns shortest path or None if no path exists"""
        ...

    def reconstruct_path(self, came_from: dict, end: Zone) -> List[Zone]:
        """Rebuild path from came_from dict"""
        ...

    def find_all_paths(self) -> List[List[Zone]]:
        """Find paths for all drones"""
        ...


# get_move_cost()     → returns 1 or 2 based on zone type
#                       (blocked should never reach here)

# find_path()         → core Dijkstra algorithm
#                       takes start and end zones
#                       returns list of zones [start → ... → end]
#                       returns None if no path found

# reconstruct_path()  → after Dijkstra finishes
#                       walks backwards through came_from
#                       builds the path list

# find_all_paths()    → calls find_path() for each drone
#                       handles distributing drones across paths
#                       returns list of paths