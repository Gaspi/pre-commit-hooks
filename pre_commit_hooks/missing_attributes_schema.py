#!/usr/bin/env python3

import argparse
import json
from collections.abc import Sequence
from typing import Generator, Tuple

def issues_in_file(file_path: str, config: dict) -> Generator[Tuple[str,str], None, None]:
    with open(file_path, 'r') as f:
        try:
            schema = json.load(f)
        except json.JSONDecodeError as e:
            return iter((([], f"Error parsing JSON: {e}"), ))
    return issues_in_schema(schema, config)

def issues_in_schema(schema, config: dict) -> Generator[Tuple[str,str], None, None]:
    def _issues(value, current_key: list[str], chk_default):
        if not isinstance(value, dict):
            yield (current_key, f"Expected object, got {type(value)}")
        elif "$ref" in value:
            pass # This object is considered a reference, not a schema
        elif "type" not in value:
            yield (current_key, "Missing 'type' attribute")
        else:
            if "default" in value:
                chk_default = False
            if value["type"] == "object":
                if "properties" in value:
                    if not isinstance(value["properties"], dict):
                        yield (current_key+["properties"], f"Expected object, got {type(value['properties'])}")
                    elif len(value["properties"]) == 0:
                        if chk_default:
                            yield (current_key, "Missing the 'default' attribute and no properties are specified to fetch defaults from")
                    else:
                        for k, v in value["properties"].items():
                            yield from _issues(v, current_key+["properties", k], chk_default)
                else:
                    if chk_default:
                        yield (current_key, "Missing the 'default' attribute and no properties are specified to fetch defaults from")
                    if "patternProperties" in value:
                        pass
                    elif "additionalProperties" in value:
                        if isinstance(value["additionalProperties"], dict):
                            yield from _issues(value["additionalProperties"], current_key+["additionalProperties"], False)
                    else:
                        if config.check_properties:
                            yield (current_key, "Missing 'properties', 'patternProperties' or 'additionalProperties' attribute in object")
            else:
                if chk_default:
                    # No default was provided
                    yield (current_key, "Missing the 'default' attribute of non-object type")
                if value["type"] == "array":
                    if "items" in value:
                        yield from _issues(value["items"], current_key+["items"], chk_default)
                    elif config.check_items:
                        yield (current_key, "Missing 'items' attribute in array")
    return _issues(schema, [], config.check_default)

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
