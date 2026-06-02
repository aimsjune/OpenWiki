import json
import sys
from pathlib import Path


class Config:
    def __init__(self, port: int = 8080, verbose: bool = False):
        self.port = port
        self.verbose = verbose


def load_config(path: str) -> Config:
    try:
        data = Path(path).read_text()
        raw = json.loads(data)
        return Config(port=raw.get("port", 8080), verbose=raw.get("verbose", False))
    except FileNotFoundError:
        print(f"config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"invalid config: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    cfg = load_config("config.json")
    print(f"server starting on port {cfg.port}")


if __name__ == "__main__":
    main()
