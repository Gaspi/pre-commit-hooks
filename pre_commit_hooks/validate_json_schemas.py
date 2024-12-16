#!/usr/bin/env python3

import argparse
import json
import sys
from jsonschema.validators import validator_for
from jsonschema import ValidationError
from collections.abc import Sequence
from typing import Generator, Tuple

def issue_in_file(file_path: str, forbid_legacy=True):
    with open(file_path, 'r') as f:
        try:
            json_content = json.load(f)
        except json.JSONDecodeError as e:
            return f"Error parsing JSON: {e}"
    if "$schema" not in json_content:
        return f"Missing `$schema` attribute"
    schema = json_content["$schema"]
    if not isinstance(schema, str):
        return "The `$schema` attribute should be a string"
    if forbid_legacy and schema in("http://json-schema.org/schema#", "http://json-schema.org/schema"):
        return "Legacy `$schema` used. Use Draft 7 instead (http://json-schema.org/draft-07/schema#)"
    try:
        validator_for(json_content).check_schema(json_content)
    except SchemaError as e:
        return f"Schema validation error: {e}"

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    parser.add_argument(
        '--forbid-legacy',
        action='store_true',
        dest='forbid_legacy',
        help='Forbids legacy https://json-schema.org/draft/2020-12/schema schema validator',
    )
    args = parser.parse_args(argv)

    retval  = 0
    for filename in args.filenames:
        issue = issue_in_file(filename, forbid_legacy=args.forbid_legacy)
        if issue:
            print(f"{filename}: {issue}")
            retval = 1
    return retval

if __name__ == "__main__":
    raise SystemExit(main())
