# from parser import Parser
# from pathlib import Path


# def main():
#     base = Path(__file__).parent
#     file_path = base / "maps" / "easy" / "01_linear_path.txt"
#     parser = Parser()
#     parser.parse(file_path)

#     data = parser.build_map_data()

#     print("NB DRONES:", data["nb_drones"])
#     print("START:", data["start"])
#     print("END:", data["end"])

#     print("\nZONES:")
#     for name, zone in data["zones"].items():
#         print(name, zone)

#     print("\nCONNECTIONS:")
#     for conn in data["connections"]:
#         print(conn)


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as e:
#         print(e)



# # from parser import Parser
# # from models import Zone, MapData, Connection

# # parser = Parser()
# # parser.parse("map.txt")
# # data = parser.build_map_data()


# # zones_objs = {name: Zone(**z) for name, z in data['zones'].items()}


from pathlib import Path
from parser import Parser
from graph import build_graph


def main():
    base = Path(__file__).parent
    file_path = base / "maps" / "easy" / "01_linear_path.txt"

    # ---- PARSE FILE ----
    parser = Parser()
    parser.parse(file_path)
    data = parser.build_map_data()

    # ---- BUILD GRAPH ----
    map_data = build_graph(data)

    # ---- PRINT RESULTS ----
    print("NB DRONES:", map_data.nb_drones)
    print("START:", map_data.start_zone.name)
    print("END:", map_data.end_zone.name)

    print("\nZONES:")
    for z in map_data.zones.values():
        print(f"{z.name} -> ({z.x}, {z.y}) max={z.max_drones} type={z.zone_type}")

    print("\nCONNECTIONS:")
    for c in map_data.connections:
        print(f"{c.zoneA.name} <-> {c.zoneB.name} cap={c.max_link_capacity}")

    print("\nNEIGHBORS:")
    for name, neighbors in map_data.neighbors.items():
        print(name, "->", [n.name for n in neighbors])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
