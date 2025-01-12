"""Parse a .vents file as produced by the SourceViewer-CLI."""

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
import json

VentsValue = str | int | float | bool | tuple[float, ...]


@dataclass
class Position:
    """Simple class."""

    x: float
    y: float
    z: float


@dataclass
class Spawns:
    """Spawns of a map."""

    CT: list[Position]
    T: list[Position]

    def to_dict(self) -> dict[str, list[dict[str, float]]]:
        """Converts the spawns to a dictionary."""
        return {
            "CT": [{"x": ct.x, "y": ct.y, "z": ct.z} for ct in self.CT],
            "T": [{"x": t.x, "y": t.y, "z": t.z} for t in self.T],
        }

    def to_json(self, path: str | Path) -> None:
        """Writes the spawns data to a JSON file.

        Args:
            path: Path to the JSON file to write.
        """
        spawns_dict = self.to_dict()
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(spawns_dict, json_file)

    @staticmethod
    def from_vents_content(vents_content: str) -> "Spawns":
        """Parse the content of a vents file into Spawns information."""
        parsed_data = parse_file_to_dict(vents_content)

        return filter_data(parsed_data)

    @staticmethod
    def from_vents_file(vents_file: str | Path) -> "Spawns":
        """Parse the content of a vents file into Spawns information."""
        with open(vents_file) as f:
            return Spawns.from_vents_content(f.read())


def parse_file_to_dict(file_content: str) -> dict[int, dict[str, VentsValue]]:
    """Parse the file content."""
    # Dictionary to hold parsed data
    parsed_data: dict[int, dict[str, VentsValue]] = {}
    block_id = 0
    block_content: dict[str, VentsValue] = {}

    for line in file_content.splitlines():
        if match := re.match(r"^====(\d+)====$", line):
            block_id = int(match.group(1))
            block_content = {}
            continue

        if not line.strip():
            continue
        try:
            key, value = line.split(maxsplit=1)
        except Exception:  # noqa: S112
            continue
        key = key.strip()
        value = value.strip()

        # Attempt to parse the value
        if value in ("True", "False"):
            value = value == "True"  # Convert to boolean
        elif re.match(r"^-?\d+$", value):
            value = int(value)  # Convert to integer
        elif re.match(r"^-?\d*\.\d+$", value):
            value = float(value)  # Convert to float
        elif re.match(r"^-?\d*\.\d+(?:\s-?\d*\.\d+)+$", value):
            value = tuple(map(float, value.split()))  # Convert to tuple of floats

        block_content[key] = value

        parsed_data[block_id] = block_content

    return parsed_data


def filter_data(data: dict[int, dict[str, VentsValue]]) -> Spawns:
    """Filter the data to get the positions."""
    ct_spawns: list[Position] = []
    t_spawns: list[Position] = []

    for properties in data.values():
        if (
            properties.get("classname") == "info_player_terrorist"
            and properties.get("enabled")
            and properties.get("priority") == 0
        ):
            x, y, z = properties["origin"]  # pyright: ignore[reportGeneralTypeIssues]
            t_spawns.append(
                Position(x=x, y=y, z=z)  # pyright: ignore[reportArgumentType]
            )
        elif (
            properties.get("classname") == "info_player_counterterrorist"
            and properties.get("enabled")
            and properties.get("priority") == 0
        ):
            x, y, z = properties["origin"]  # pyright: ignore[reportGeneralTypeIssues]
            ct_spawns.append(
                Position(x=x, y=y, z=z)  # pyright: ignore[reportArgumentType]
            )

    return Spawns(CT=ct_spawns, T=t_spawns)





def main() -> None:
    # Create the parser
    parser = argparse.ArgumentParser(description="Process a file path.")

    # Add the file path argument
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to the input file"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Validate the file path
    if not os.path.isfile(args.file_path):
        print(f"Error: The file '{args.file_path}' does not exist.")
        return
    # Example usage
    vent_file = args.file_path
    output_path = vent_file.with_suffix(".json")
    spawns_data = Spawns.from_vents_file(vent_file)
    spawns_data.to_json(path=output_path)
    print(spawns_data)
    print(len(spawns_data.CT), len(spawns_data.T))


if __name__ == "__main__":
    main()