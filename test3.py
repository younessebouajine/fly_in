import re
from typing import Any
from exceptions import ParseError

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
    r"(\w+)\s*=\s*([^\s\]=]+)",
    re.IGNORECASE
)


class Parser:
    def __init__(self) -> None:
        self.nb_drones: int | None = None
        self.zones: dict[str, dict[str, Any]] = {}
        self.connections: list[dict[str, Any]] = []
        self.start_zone: str | None = None
        self.end_zone: str | None = None
        self.seen_edges: set[tuple[str, str]] = set()

    def parse(self, file_path: str) -> None:
        with open(file_path, "r") as file:
            for line_number, line in enumerate(file, start=1):
                clean = self.clean_line(line)
                if not clean:
                    continue
                self.parse_line(clean, line_number)

        self.final_validate()

    def clean_line(self, line: str) -> str:
        line = line.strip()
        if not line or line.startswith("#"):
            return ""
        return line.split("#")[0].strip()

    def parse_line(self, line: str, line_no: int) -> None:
        lower = line.lower()

        if self.nb_drones is None and not lower.startswith("nb_drones"):
            raise ParseError(f"Line {line_no}: nb_drones must come first")

        if lower.startswith("nb_drones:"):
            self.parse_nb_drones(line, line_no)
        elif lower.startswith(("start_hub:", "hub:", "end_hub:")):
            self.parse_zone(line, line_no)
        elif lower.startswith("connection:"):
            self.parse_connection(line, line_no)
        else:
            raise ParseError(f"Line {line_no}: unknown line format")

    def parse_nb_drones(self, line: str, line_no: int) -> None:
        if self.nb_drones is not None:
            raise ParseError(f"Line {line_no}: nb_drones duplicated")

        match = NB_DRONES_RE.match(line)
        if not match:
            raise ParseError(f"Line {line_no}: invalid nb_drones")

        value = int(match.group(1))
        if value <= 0:
            raise ParseError(f"Line {line_no}: nb_drones must be > 0")

        self.nb_drones = value

    def parse_zone(self, line: str, line_no: int) -> None:
        match = ZONE_RE.match(line)
        if not match:
            raise ParseError(f"Line {line_no}: invalid zone syntax")

        typezone, name, x, y, metadata = match.groups()

        if name in self.zones:
            raise ParseError(f"Line {line_no}: duplicate zone '{name}'")

        meta = self.parse_metadata(metadata or "", line_no, line)

        zone_type = meta.get("zone", "normal").lower()
        if zone_type not in {"normal", "blocked", "restricted", "priority"}:
            raise ParseError(f"Line {line_no}: invalid zone type")

        max_drones = int(meta.get("max_drones", 1))
        if max_drones <= 0:
            raise ParseError(f"Line {line_no}: max_drones must be > 0")

        if typezone in ("start_hub", "end_hub"):
            max_drones = self.nb_drones  # override

        self.zones[name] = {
            "type": typezone,
            "name": name,
            "x": int(x),
            "y": int(y),
            "zone_type": zone_type,
            "color": meta.get("color"),
            "max_drones": max_drones
        }

        if typezone == "start_hub":
            if self.start_zone:
                raise ParseError(f"Line {line_no}: multiple start_hub")
            self.start_zone = name

        if typezone == "end_hub":
            if self.end_zone:
                raise ParseError(f"Line {line_no}: multiple end_hub")
            self.end_zone = name

    def parse_connection(self, line: str, line_no: int) -> None:
        match = CONNECTION_RE.match(line)
        if not match:
            raise ParseError(f"Line {line_no}: invalid connection")

        z1, z2, metadata = match.groups()

        if z1 not in self.zones or z2 not in self.zones:
            raise ParseError(f"Line {line_no}: undefined zone")

        if z1 == z2:
            raise ParseError(f"Line {line_no}: self connection")

        edge = tuple(sorted((z1, z2)))
        if edge in self.seen_edges:
            raise ParseError(f"Line {line_no}: duplicate connection")

        meta = self.parse_metadata(metadata or "", line_no, line)

        capacity = int(meta.get("max_link_capacity", 1))
        if capacity <= 0:
            raise ParseError(f"Line {line_no}: invalid capacity")

        self.connections.append({
            "from": z1,
            "to": z2,
            "capacity": capacity
        })

        self.seen_edges.add(edge)

    def parse_metadata(self, text: str, line_no: int, line: str) -> dict[str, str]:
        result: dict[str, str] = {}

        if not text:
            return result

        for key, value in METADATA_ITEM_RE.findall(text):
            result[key.lower()] = value

        return result

    def final_validate(self) -> None:
        if self.nb_drones is None:
            raise ParseError("nb_drones missing")
        if not self.start_zone:
            raise ParseError("start_hub missing")
        if not self.end_zone:
            raise ParseError("end_hub missing")
        if not self.connections:
            raise ParseError("no connections")

    def build_map_data(self) -> dict[str, Any]:
        return {
            "nb_drones": self.nb_drones,
            "zones": self.zones,
            "connections": self.connections,
            "start": self.start_zone,
            "end": self.end_zone
        }
