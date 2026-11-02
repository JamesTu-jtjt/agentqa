"""Package only the current repository's Git-visible source/evidence files."""

import argparse
import json
from pathlib import Path

from agentqa.distribution import create_bundle, verify_archive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = create_bundle(root, args.output)
    print(json.dumps({**verify_archive(args.output), "secret_pattern_findings": manifest["secret_pattern_findings"]}))


if __name__ == "__main__":
    main()
