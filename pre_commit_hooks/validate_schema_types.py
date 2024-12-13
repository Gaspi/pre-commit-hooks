#!/usr/bin/env python3

import argparse
import json
import os
import sys
from collections.abc import Sequence
from typing import Generator, Tuple

def issues_in_file(file_path: str, config: dict) -> Generator[Tuple[str,str], None, None]:
    with open(file_path, 'r') as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            return iter(( ([], f"Error parsing JSON: {e}") ))
    return issues_in_schema(schema, config)

def issues_in_schema(schema, config: dict) -> Generator[Tuple[str,str], None, None]:
    def _issues(value, current_key: list[str] = []):
        if not isinstance(value, dict):
            yield (current_key, f"Expected object, got {type(value)}")
        elif "type" not in value:
            yield (current_key, "Missing 'type' attribute")
        else:
            if config.check_default and "default" not in value:
                yield (current_key, "Missing 'default' attribute")
            if value["type"] == "object":
                if config.check_properties and "properties" not in value:
                    yield (current_key, "Missing 'properties' attribute")
                elif "properties" in value:
                    if not isinstance(value["properties"], dict):
                        yield (current_key+["properties"], f"Expected object, got {type(value['properties'])}")
                    else:
                        for key, value in value["properties"].items():
                            yield from _issues(value, current_key+["properties", key])
            if value["type"] == "array":
                if "items" in value:
                    yield from _issues(value["items"], current_key+["items"])
                elif config.check_items:
                    yield (current_key, "Missing 'items' attribute in array")
    return _issues(schema, [])

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    parser.add_argument(
        '--check-default',
        action='store_true',
        dest='check_default',
        help='Require defaults to be systematically specified',
    )
    parser.add_argument(
        '--check-properties',
        action='store_true',
        dest='check_properties',
        help='Require properties to be systematically specified for object',
    )
    parser.add_argument(
        '--check-items',
        action='store_true',
        dest='check_items',
        help='Require items to be systematically specified for arrays',
    )
    args = parser.parse_args(argv)

    all_valid = True
    for schema_file in args.filenames:
        for key, issue in issues_in_file(schema_file, args):
            print(f"In file {schema_file}, at key {'.'.join(key) or '[root]'}: {issue}")
            all_valid = False
    return 1 if not all_valid else 0

if __name__ == "__main__":
    raise SystemExit(main())
