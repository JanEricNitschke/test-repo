import subprocess
import sys
from datetime import datetime, timezone
import re
import vdf

TIME_FILE = "last_run_time.txt"


def get_current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


def read_last_run_time() -> str:
    with open(TIME_FILE, "r") as f:
        return f.read().strip()


def write_last_run_time(utc_time):
    with open(TIME_FILE, "w") as f:
        f.write(utc_time)
        f.write("\n")


def needs_regeneration(last_run_time: datetime, last_update_time: datetime) -> bool:
    return last_run_time < last_update_time


def get_last_update_time() -> datetime:
    command = [
        "steamcmd",
        "+login",
        "anonymous",
        "+app_info_print",
        "730",
        "+logoff",
        "+quit",
    ]

    # Run the command and capture the output
    result = subprocess.check_output(command).decode("utf-8")
    json_start = result.find("730")
    json_end_index = result.rfind("}")
    vdf_data = result[json_start : json_end_index + 1]
    vdf_data = re.sub(r'^(?!\s*[{}]|.*".*").*$', '', vdf_data, flags=re.M)
    parsed_data = vdf.loads(vdf_data)

    timeline_marker_updated = int(parsed_data["730"]["common"]["timeline_marker_updated"])

    return datetime.fromtimestamp(timeline_marker_updated, timezone.utc)


def main():
    last_run_time = datetime.fromisoformat(read_last_run_time())
    last_update_time = get_last_update_time()

    if last_run_time and needs_regeneration(
        last_run_time=last_run_time, last_update_time=last_update_time
    ):
        print("Regenerate timestamp.")
        write_last_run_time(get_current_utc_time().isoformat())
        print("Regeneration complete.")
        sys.exit(0)
    else:
        print("No update since last run.")
        sys.exit(2)


if __name__ == "__main__":
    main()
