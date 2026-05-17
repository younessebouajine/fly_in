from pathfinding import PathFinder
from models import MapData, Drone, Zone, Connection


class Simulation:
    def __init__(self, map_data: MapData):
        self.map_data = map_data
        self.pathfinder = PathFinder(map_data)

        self.drones: list[Drone] = []

        self.current_turn = 0

        self.create_drones()
        self.assign_paths()

    def create_drones(self) -> None:
        """
        Create all drones at the start zone.
        """

        start_zone = self.map_data.start_zone

        if self.map_data.nb_drones > start_zone.max_drones:
            raise ValueError(
                "Number of drones exceeds start zone capacity"
            )

        for i in range(self.map_data.nb_drones):

            drone = Drone(
                drone_id=i + 1,
                start_zone=start_zone
            )

            self.drones.append(drone)

            start_zone.drones.append(drone)

    def assign_paths(self) -> None:
        """
        Give a path to every drone.
        """

        all_paths = self.pathfinder.find_all_paths()

        for drone, path in zip(self.drones, all_paths):

            # Give every drone its own copy
            drone.path = path[:]

    def run(self) -> None:
        """
        Run simulation until all drones reach end zone.
        """

        print("\n=== SIMULATION START ===\n")

        while not self.all_drones_arrived():

            self.current_turn += 1

            print(f"\n--- TURN {self.current_turn} ---")

            self.move_drones()

            self.reset_connections()

        print("\n=== SIMULATION FINISHED ===")

    def move_drones(self) -> None:
        """
        Move all drones one step if possible.
        """

        for drone in self.drones:

            # Already arrived
            if drone.current_zone == self.map_data.end_zone:
                continue

            # Waiting inside restricted zone
            if drone.turns_remaining > 0:

                drone.turns_remaining -= 1

                print(
                    f"Drone {drone.drone_id} waiting "
                    f"({drone.turns_remaining} turns left)"
                )

                continue

            # Safety check
            if drone.path_index >= len(drone.path) - 1:
                continue

            # Next destination
            next_zone = drone.path[drone.path_index + 1]

            # Cannot enter blocked zone
            if next_zone.zone_type == "blocked":

                print(
                    f"Drone {drone.drone_id} "
                    f"cannot enter blocked zone"
                )

                continue

            # Zone capacity
            if (
                next_zone != self.map_data.end_zone
                and next_zone.is_full()
            ):

                print(
                    f"Drone {drone.drone_id} waits "
                    f"(zone {next_zone.name} is full)"
                )

                continue

            # Connection lookup
            connection = self.get_connection(
                drone.current_zone,
                next_zone
            )

            if connection is None:
                continue

            # Connection capacity
            if (
                connection.current_transit
                >= connection.max_link_capacity
            ):

                print(
                    f"Drone {drone.drone_id} waits "
                    f"(connection full)"
                )

                continue

            # Move drone
            old_zone = drone.current_zone

            old_zone.drones.remove(drone)

            next_zone.drones.append(drone)

            drone.current_zone = next_zone

            drone.path_index += 1

            connection.current_transit += 1

            print(
                f"Drone {drone.drone_id}: "
                f"{old_zone.name} -> {next_zone.name}"
            )

            # Restricted zones require extra waiting turn
            if next_zone.zone_type == "restricted":

                drone.turns_remaining = 1

    def get_connection(
        self,
        zone_a: Zone,
        zone_b: Zone
    ) -> Connection | None:
        """
        Return connection between two zones.
        """

        for connection in self.map_data.connections:

            if connection.connects(zone_a.name, zone_b.name):

                return connection

        return None

    def reset_connections(self) -> None:
        """
        Reset transit counters every turn.
        """

        for connection in self.map_data.connections:

            connection.current_transit = 0

    def all_drones_arrived(self) -> bool:
        """
        Return True if all drones reached end zone.
        """

        for drone in self.drones:

            if drone.current_zone != self.map_data.end_zone:

                return False

        return True
