from parser import Parser
from pathlib import Path


def main():
    base = Path(__file__).parent
    file_path = base / "maps" / "easy" / "01_linear_path.txt"
    parser = Parser()
    parser.parse(file_path)

    data = parser.build_map_data()

    print("NB DRONES:", data["nb_drones"])
    print("START:", data["start"])
    print("END:", data["end"])

    print("\nZONES:")
    for name, zone in data["zones"].items():
        print(name, zone)

    print("\nCONNECTIONS:")
    for conn in data["connections"]:
        print(conn)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)



# from parser import Parser
# from models import Zone, MapData, Connection

# parser = Parser()
# parser.parse("map.txt")
# data = parser.build_map_data()


# zones_objs = {name: Zone(**z) for name, z in data['zones'].items()}
