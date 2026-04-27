from typing import List


class Zone:
    def __init__(self, name: str, x: int, y: int, max_drones: int,
                 zone_type: str, color: str) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.max_drones = max_drones
        self.zone_type = zone_type
        self.color = color
        self.drones: List["Drone"] = []     # nb of drones in this zone

    def is_zone_full(self) -> bool:
        """Check if the area has reached its maximum capacity"""
        return len(self.drones) >= self.max_drones


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone,
                 max_link_capacity: int) -> None:
        self.zones = {zone_a.name: zone_a, zone_b.name: zone_b}
        self.max_link_capacity = max_link_capacity
        self.current_transit_count = 0


class Drone:
    def __init__(self, drone_id: int, current_zone: Zone) -> None:
        self.drone_id = drone_id
        self.start_zone = current_zone
        self.path: List[Zone] = []


class MapData:
    def __init__(self, nb_drones: int, zones: dict[str, Zone],
                 connections: List[Connection],
                 start_name: str, end_name: str):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        self.start_zone = zones[start_name]
        self.end_zone = zones[end_name]
        self.neighbors: dict[str, List[Zone]] = self.build_neighbors()

    def build_neighbors(self) -> dict[str, List[Zone]]:
        adj = {name: [] for name in self.zones}
        for conn in self.connections:
            z1, z2 = list(conn.zones.values())
            adj[z1.name].append(z2)
            adj[z2.name].append(z1)
        return adj
