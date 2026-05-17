import heapq
from typing import List, Optional
from models import Zone, MapData


class PathFinder:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data

    def get_move_cost(
        self,
        zone: Zone,
        penalized_zones: set[str]
    ) -> int:
        """
        Return movement cost based on zone type.

        Restricted zones cost more.
        Penalized zones get extra cost so Dijkstra
        prefers different paths.
        """

        cost = 1

        if zone.zone_type == "restricted":
            cost = 2

        if zone.name in penalized_zones:
            cost += 5

        return cost

    def find_path(
        self,
        start: Zone,
        end: Zone,
        penalized_zones: set[str]
    ) -> Optional[List[Zone]]:
        """
        Find shortest path using Dijkstra.
        """

        distances: dict[str, float] = {
            zone_name: float("inf")
            for zone_name in self.map_data.zones
        }

        distances[start.name] = 0

        came_from: dict[str, str] = {}

        priority_queue: list[tuple[float, str]] = [
            (0, start.name)
        ]

        visited: set[str] = set()

        while priority_queue:

            current_distance, current_name = heapq.heappop(
                priority_queue
            )

            if current_name in visited:
                continue

            visited.add(current_name)

            if current_name == end.name:
                return self.reconstruct_path(
                    came_from,
                    end
                )

            current_zone = self.map_data.zones[current_name]

            for neighbor in self.map_data.neighbors[current_name]:

                if neighbor.zone_type == "blocked":
                    continue

                move_cost = self.get_move_cost(
                    neighbor,
                    penalized_zones
                )

                new_distance = current_distance + move_cost

                if new_distance < distances[neighbor.name]:

                    distances[neighbor.name] = new_distance

                    came_from[neighbor.name] = current_name

                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbor.name)
                    )

        return None

    def reconstruct_path(
        self,
        came_from: dict[str, str],
        end: Zone
    ) -> List[Zone]:

        path = []

        current_name = end.name

        while current_name in came_from:

            current_zone = self.map_data.zones[current_name]

            path.append(current_zone)

            current_name = came_from[current_name]

        start_zone = self.map_data.zones[current_name]

        path.append(start_zone)

        path.reverse()

        return path

    def find_all_paths(self) -> List[List[Zone]]:
        """
        Find multiple paths and distribute drones across them.
        """

        start = self.map_data.start_zone
        end = self.map_data.end_zone

        all_paths: List[List[Zone]] = []

        used_paths: set[tuple[str, ...]] = set()

        penalized_zones: set[str] = set()

        while True:

            path = self.find_path(
                start,
                end,
                penalized_zones
            )

            if path is None:
                break

            path_key = tuple(
                zone.name
                for zone in path
            )

            if path_key in used_paths:
                break

            used_paths.add(path_key)

            all_paths.append(path)

            for zone in path[1:-1]:
                penalized_zones.add(zone.name)

        if not all_paths:
            return []

        drone_paths = []

        for i in range(self.map_data.nb_drones):

            selected_path = all_paths[
                i % len(all_paths)
            ]

            drone_paths.append(selected_path)

        return drone_paths
