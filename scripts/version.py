"""Aria release version source of truth and deterministic version bump CLI."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILE = ROOT / "version.json"


def read_version(path=DEFAULT_FILE):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"major", "minor"}:
        raise ValueError("Version must contain only integer major and minor fields")
    if any(type(data[field]) is not int or data[field] < 0 for field in ("major", "minor")):
        raise ValueError("Version numbers must be nonnegative integers")
    return data


def display_version(version):
    return f"{version['major']}.{version['minor']}"


def next_version(version, part):
    if part == "minor":
        return {"major": version["major"], "minor": version["minor"] + 1}
    if part == "major":
        return {"major": version["major"] + 1, "minor": 0}
    raise ValueError(f"Unsupported bump: {part}")


def main():
    parser = argparse.ArgumentParser(description="Aria app release version")
    parser.add_argument("action", choices=["show", "bump"])
    parser.add_argument("--part", choices=["minor", "major"], default="minor")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE)
    args = parser.parse_args()
    version = read_version(args.file)
    if args.action == "bump":
        version = next_version(version, args.part)
        args.file.write_text(json.dumps(version, indent=2) + "\n", encoding="utf-8")
    print(display_version(version))


if __name__ == "__main__":
    main()
