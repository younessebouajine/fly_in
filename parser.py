import re
from exceptions import ParseError
from typing import Any


NB_DRONES_RE = re.compile(
    r"^nb_drones\s*:\s*(\d+)\s*$",
    re.IGNORECASE
)

ZONE_RE = re.compile(
    r"^(start_hub|end_hub|hub)\s*:\s*([^\s\-\[\]]+)\s+(-?\d+)\s+(-?\d+)\s*(?:\[\s*(.*?)\s*\])?\s*$",
    re.IGNORECASE
)

CONNECTION_RE = re.compile(
    r"^connection\s*:\s*([^\s\-\[\]]+)\s*-\s*([^\s\-\[\]]+)\s*(?:\[\s*(.*?)\s*\])?\s*$",
    re.IGNORECASE
)

METADATA_ITEM_RE = re.compile(
    r"(\w+)\s*=\s*([^\s\]]+)",
    re.IGNORECASE
)


class Parser:
    def __init__(self) -> None:
        self.nb_drones = None
        self.zones = {}
        self.connections = []
        self.start_zone = None
        self.end_zone = None
        self.seen_edges = set()

    def parse(self, file_path: str):
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                _clean_line = self.clean_line(line)
                if _clean_line == "":
                    continue
                else:
                    self.parse_line(_clean_line, line_number)

    def clean_line(self, line: str) -> str:
        if not line or line.startswith("#"):
            return ""
        else:
            new_line = line.split('#')[0].strip()
            return new_line

    def parse_line(self, line: str, line_no: int) -> None:
        if line.startswith("nb_drones:"):
            self.parse_nb_drones(line, line_no)
        elif line.startswith("start_hub:") or \
                line.startswith("hub:") or line.startswith("end_hub:"):
            self.parse_zone_line(line, line_no)
        elif line.startswith("connection:"):
            self.parse_connection_line(line, line_no)
        else:
            raise ParseError(
                f"line number {line_no} is envalid line,"
                " Enter a suitable line"
                )

    def parse_nb_drones(self, line: str, line_no: int) -> None:
        if self.nb_drones is not None:
            raise ParseError(
                f"Error on line {line_no}: nb_drones is defined more than once"
            )

        match = NB_DRONES_RE.match(line)
        if not match:
            raise ParseError(
                f"Error on line {line_no}: invalid nb_drones syntax"
            )

        value = int(match.group(1))

        if value <= 0:
            raise ParseError(
                f"Error on line {line_no}: "
                "nb_drones must be a positive integer"
            )

        self.nb_drones = value

    def parse_zone_line(self, line: str, line_no: int) -> None:
        meta_data: dict[Any, Any] = {}
        final_dict = {}

        match = ZONE_RE.match(line)
        if not match:
            raise ParseError(
                f"Error on line {line_no}: invalid zone line syntax"
            )

        typezone = match.group(1)
        name = match.group(2)
        x = int(match.group(3))
        y = int(match.group(4))

        if match.group(5) is not None:
            metadata_text = match.group(5)
            meta_data = self.parse_metadata(metadata_text, line_no)

        if "zone" not in meta_data:
            meta_data["zone"] = "normal"
        if "color" not in meta_data:
            meta_data["color"] = None
        if "max_drones" not in meta_data:
            meta_data["max_drones"] = 1

        types_zone = ["normal", "blocked", "restricted", "priority"]
        zone_type = meta_data.get("zone")
        if zone_type not in types_zone:
            raise ParseError(
                f"Error on line {line_no}: invalid zone type '{zone_type}'"
            )

        color = meta_data.get("color")

        try:
            max_drones = int(meta_data.get("max_drones"))
        except (ValueError, TypeError):
            raise ParseError(
                f"Error on line {line_no}: max_drones must be a valid integer"
            )

        if max_drones <= 0:
            raise ParseError(
                f"Error on line {line_no}: "
                "max_drones must be a positive integer"
            )

        if name in self.zones:
            raise ParseError(
                f"Error on line {line_no}: "
                f"zone '{name}' is defined more than once"
            )

        final_dict.update({
            "typezone": typezone,
            "name": name,
            "x": x,
            "y": y,
            "zone_type": zone_type,
            "color": color,
            "max_drones": max_drones
        })

        self.zones[name] = final_dict

        if typezone == "start_hub":
            if self.start_zone is None:
                self.start_zone = name
            else:
                raise ParseError(
                    f"Error on line {line_no}: "
                    "start_hub is defined more than once"
                )

        if typezone == "end_hub":
            if self.end_zone is None:
                self.end_zone = name
            else:
                raise ParseError(
                    f"Error on line {line_no}: "
                    "end_hub is defined more than once"
                )

    def parse_metadata(self, metadata_text: str,
                       line_no: int) -> dict[str, str]:
        meta_data_dict: dict[str, str] = {}
        if not metadata_text:
            return meta_data_dict
        matches = METADATA_ITEM_RE.findall(metadata_text)
        if not matches:
            raise ParseError(
                f"Error on line {line_no}: invalid metadata syntax"
            )
        for key, value in matches:
            meta_data_dict[key.lower()] = value
        return meta_data_dict

    def validate_zone(self, zone, line_no: int) -> None:
        pass

    def register_zone(self, zone, zone_kind: str, line_no: int) -> None:
        pass

    def parse_connection_line(self, line: str, line_no: int) -> None:
        match = CONNECTION_RE.match(line)
        

    def validate_connection(self, connection, line_no: int) -> None:
        pass

    def register_connection(self, connection) -> None:
        pass

    def final_validate(self) -> None:
        pass

    def build_map_data(self):
        pass
