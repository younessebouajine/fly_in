from typing import List


class Zone:
    def __init__(self, name: str, x: int, y: int, max_drones: int,
                 zone_type: str, color: str | None) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.max_drones = max_drones
        self.zone_type = zone_type
        self.color = color
        self.drones: List["Drone"] = []     # all drones currently inside the zone

    def is_full(self) -> bool:
        """Check if the area has reached its maximum capacity"""
        return len(self.drones) >= self.max_drones


class Connection:
    def __init__(self, zoneA: Zone, zoneB: Zone,
                 max_link_capacity: int) -> None:
        self.zoneA = zoneA
        self.zoneB = zoneB
        self.max_link_capacity = max_link_capacity # Limits how many drones can pass at the same time
        self.current_transit = 0 # how many drones are currently using this connection

    def connects(self, zone1: str, zone2: str) -> bool:
        """Checks if this connection links two zones""" 
        return (
            (self.zoneA.name == zone1 and self.zoneB.name == zone2)
            or
            (self.zoneA.name == zone2 and self.zoneB.name == zone1)
        )
        # {self.zoneA.name, self.zoneB.name} == {zone1, zone2}



class Drone:
    def __init__(self, drone_id: int, start_zone: Zone) -> None:
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.path: List[Zone] = []
        self.in_transit = False # Is drone currently moving
        self.turns_remaining = 0  # this for restricted zones


class MapData:
    """Represents the entire graph"""
    def __init__(self, nb_drones: int, zones: dict[str, Zone],
                 connections: List[Connection],
                 start: str, end: str):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        self.start_zone = zones[start]
        self.end_zone = zones[end]
        self.neighbors: dict[str, List[Zone]] = self.build_neighbors()

    def build_neighbors(self) -> dict[str, List[Zone]]:
        adj = {name: [] for name in self.zones}
        for conn in self.connections:
            adj[conn.zoneA.name].append(conn.zoneB)
            adj[conn.zoneB.name].append(conn.zoneA)
        return adj


# # from typing import List, Optional


# class Zone:
#     def __init__(
#         self,
#         name: str,
#         x: int,
#         y: int,
#         max_drones: int,
#         zone_type: str,
#         color: Optional[str]
#     ) -> None:
#         self.name = name
#         self.x = x
#         self.y = y
#         self.max_drones = max_drones
#         self.zone_type = zone_type
#         self.color = color

#         # runtime state
#         self.drones: List["Drone"] = []

#     def is_full(self) -> bool:
#         return len(self.drones) >= self.max_drones

#     def __repr__(self) -> str:
#         return f"Zone({self.name})"


# class Connection:
#     def __init__(
#         self,
#         zoneA: Zone,
#         zoneB: Zone,
#         max_link_capacity: int
#     ) -> None:
#         self.zoneA = zoneA
#         self.zoneB = zoneB
#         self.max_link_capacity = max_link_capacity

#         # runtime state
#         self.current_transit = 0

#     def other(self, zone: Zone) -> Zone:
#         """Return the opposite zone"""
#         if zone == self.zoneA:
#             return self.zoneB
#         return self.zoneA

#     def is_available(self) -> bool:
#         return self.current_transit < self.max_link_capacity

#     def __repr__(self) -> str:
#         return f"{self.zoneA.name} <-> {self.zoneB.name}"


# class Drone:
#     def __init__(self, drone_id: int, start_zone: Zone) -> None:
#         self.id = drone_id

#         # position
#         self.current_zone: Optional[Zone] = start_zone
#         self.current_connection: Optional[Connection] = None

#         # movement state
#         self.turns_remaining = 0  # for restricted zones

#         # path (precomputed)
#         self.path: List[Zone] = []
#         self.path_index = 0

#     def is_moving(self) -> bool:
#         return self.current_connection is not None

#     def __repr__(self) -> str:
#         return f"D{self.id}"


# class MapData:
#     def __init__(
#         self,
#         nb_drones: int,
#         zones: dict[str, Zone],
#         connections: List[Connection],
#         start: str,
#         end: str
#     ) -> None:
#         self.nb_drones = nb_drones
#         self.zones = zones
#         self.connections = connections

#         self.start_zone = zones[start]
#         self.end_zone = zones[end]

#         # adjacency WITH connection info (important)
#         self.neighbors: dict[str, List[tuple[Zone, Connection]]] = \
#             self.build_neighbors()

#     def build_neighbors(self) -> dict[str, List[tuple[Zone, Connection]]]:
#         adj: dict[str, List[tuple[Zone, Connection]]] = {
#             name: [] for name in self.zones
#         }

#         for conn in self.connections:
#             adj[conn.zoneA.name].append((conn.zoneB, conn))
#             adj[conn.zoneB.name].append((conn.zoneA, conn))

#         return adj