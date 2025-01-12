"""Parse a .vents file as produced by the SourceViewer-CLI."""

import argparse
import os
import re
from dataclasses import dataclass

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
    with open(args.file_path) as file:
        file_content = file.read()

    parsed_data = parse_file_to_dict(file_content)

    filtered_data = filter_data(parsed_data)

    print(filtered_data)
    print(len(filtered_data.CT), len(filtered_data.T))


if __name__ == "__main__":
    main()