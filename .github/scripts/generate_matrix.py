#!/usr/bin/env python3
"""Read .github/docker-images.yml and emit a GitHub Actions JSON matrix.

Prerequisite: PyYAML must be installed before running this script.
  pip install pyyaml==6.0.1
"""

import json
import sys

try:
    import yaml
except ImportError:
    print(
        "Error: PyYAML is not installed. Run 'pip install pyyaml==6.0.1' first.",
        file=sys.stderr,
    )
    sys.exit(1)


CONFIG_PATH = ".github/docker-images.yml"


def main() -> None:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: config file '{CONFIG_PATH}' not found.", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"Error: invalid YAML in '{CONFIG_PATH}': {exc}", file=sys.stderr)
        sys.exit(1)

    images = cfg.get("images")
    if not images or not isinstance(images, list):
        print(
            f"Error: '{CONFIG_PATH}' must contain a non-empty 'images' list.",
            file=sys.stderr,
        )
        sys.exit(1)

    include = []
    for i, img in enumerate(images):
        for required in ("name", "dockerfile"):
            if not img.get(required):
                print(
                    f"Error: image entry {i} in '{CONFIG_PATH}' is missing required field '{required}'.",
                    file=sys.stderr,
                )
                sys.exit(1)
        include.append(
            {
                "image_name": img["name"],
                "dockerfile_path": img["dockerfile"],
                "context_path": img.get("context", "."),
            }
        )

    print(json.dumps({"include": include}))


if __name__ == "__main__":
    main()
