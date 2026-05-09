import heapq
from typing import List, Optional
from models import Zone, MapData, Connection


class PathFinder:
    """Handles pathfinding for all drones across the zone graph."""

    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data

    def get_move_cost(self, zone: Zone) -> int:
        """Return movement cost in turns based on destination zone type.

        Args:
            zone: The destination zone.

        Returns:
            2 for restricted zones, 1 for all others.
        """
        if zone.zone_type == "restricted":
            return 2
        return 1

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        """Retrieve the Connection object linking two zones, if it exists.

        Args:
            zone_a: First zone.
            zone_b: Second zone.

        Returns:
            The Connection linking them, or None.
        """
        for conn in self.map_data.connections:
            if conn.connects(zone_a.name, zone_b.name):
                return conn
        return None

    def find_path(self, start: Zone, end: Zone,
                  avoid_blocked: bool = True) -> Optional[List[Zone]]:
        """Dijkstra shortest path from start to end, weighted by zone type.

        Priority zones cost the same (1 turn) but are preferred by using
        a fractional tie-breaker so Dijkstra naturally picks them first.

        Args:
            start: Starting zone.
            end: Destination zone.
            avoid_blocked: If True, blocked zones are skipped entirely.

        Returns:
            Ordered list of zones from start to end (inclusive),
            or None if no valid path exists.
        """
        # heap entries: (cost, tie_breaker, zone_name)
        heap: List[tuple[float, int, str]] = []
        counter = 0
        heapq.heappush(heap, (0.0, counter, start.name))

        dist: dict[str, float] = {start.name: 0.0}
        came_from: dict[str, Optional[str]] = {start.name: None}

        while heap:
            current_cost, _, current_name = heapq.heappop(heap)

            if current_name == end.name:
                return self.reconstruct_path(came_from, end)

            # Skip if we already found a better path here
            if current_cost > dist.get(current_name, float("inf")):
                continue

            current_zone = self.map_data.zones[current_name]

            for neighbor in self.map_data.neighbors[current_name]:
                if avoid_blocked and neighbor.zone_type == "blocked":
                    continue

                move_cost = self.get_move_cost(neighbor)

                # Priority zones get a small fractional bonus so they are
                # preferred over normal zones with equal integer cost.
                if neighbor.zone_type == "priority":
                    effective_cost = current_cost + move_cost - 0.01
                else:
                    effective_cost = current_cost + move_cost

                if effective_cost < dist.get(neighbor.name, float("inf")):
                    dist[neighbor.name] = effective_cost
                    came_from[neighbor.name] = current_name
                    counter += 1
                    heapq.heappush(heap, (effective_cost, counter, neighbor.name))

        return None  # no path found

    def reconstruct_path(self, came_from: dict[str, Optional[str]],
                         end: Zone) -> List[Zone]:
        """Reconstruct the zone path by walking came_from back to the start.

        Args:
            came_from: Map of zone_name -> previous zone_name.
            end: The destination zone.

        Returns:
            Ordered list of Zone objects from start to end.
        """
        path: List[Zone] = []
        current: Optional[str] = end.name

        while current is not None:
            path.append(self.map_data.zones[current])
            current = came_from.get(current)

        path.reverse()
        return path

    def find_all_paths(self) -> List[List[Zone]]:
        """Assign a path to each drone, distributing them across available routes.

        Strategy:
          1. Collect all simple paths from start to end (up to a reasonable limit).
          2. Sort paths by cost (ascending), preferring shorter / priority-rich ones.
          3. Assign drones round-robin across the best paths so the fleet
             spreads out and bottlenecks are reduced.

        Returns:
            A list of nb_drones paths, one per drone, each being an ordered
            list of Zone objects from start to end.
        """
        start = self.map_data.start_zone
        end = self.map_data.end_zone
        nb_drones = self.map_data.nb_drones

        all_paths = self._enumerate_paths(start, end, max_paths=20)

        if not all_paths:
            # Fallback: single Dijkstra path repeated for every drone
            fallback = self.find_path(start, end)
            if fallback is None:
                return []
            return [fallback[:] for _ in range(nb_drones)]

        # Sort by weighted cost so cheaper paths come first
        all_paths.sort(key=lambda p: self._path_cost(p))

        # Distribute drones across paths (round-robin)
        drone_paths: List[List[Zone]] = []
        for i in range(nb_drones):
            drone_paths.append(all_paths[i % len(all_paths)][:])

        return drone_paths

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _path_cost(self, path: List[Zone]) -> float:
        """Compute the weighted turn cost of a path.

        Args:
            path: Ordered list of zones.

        Returns:
            Total turn cost (restricted=2, priority=0.99, normal=1).
        """
        cost = 0.0
        for zone in path[1:]:           # skip start zone (no entry cost)
            if zone.zone_type == "restricted":
                cost += 2
            elif zone.zone_type == "priority":
                cost += 0.99
            else:
                cost += 1
        return cost

    def _enumerate_paths(self, start: Zone, end: Zone,
                         max_paths: int = 20) -> List[List[Zone]]:
        """DFS enumeration of simple (non-repeating) paths from start to end.

        Blocked zones are skipped. Search is capped at max_paths to keep
        runtime bounded on large or highly connected graphs.

        Args:
            start: Source zone.
            end: Destination zone.
            max_paths: Maximum number of paths to collect.

        Returns:
            List of paths, each being an ordered list of Zone objects.
        """
        results: List[List[Zone]] = []
        visited: set[str] = set()

        def dfs(current: Zone, path: List[Zone]) -> None:
            if len(results) >= max_paths:
                return

            if current.name == end.name:
                results.append(path[:])
                return

            visited.add(current.name)

            for neighbor in self.map_data.neighbors[current.name]:
                if neighbor.name in visited:
                    continue
                if neighbor.zone_type == "blocked" and neighbor.name != end.name:
                    continue

                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()

            visited.remove(current.name)

        dfs(start, [start])
        return results