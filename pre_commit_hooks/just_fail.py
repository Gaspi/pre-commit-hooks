#!/usr/bin/env python3

import argparse
from collections.abc import Sequence

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    parser.add_argument(
        '--message',
        type=str,
        dest='message',
        help='Warning message to emit',
        default="""You are trying to push modifications to a protected file: {}.
        If everything else looks fine and you know what you are doing, use `--no-verify` to skip all checks.""",
    )
    args = parser.parse_args(argv)
    for filename in args.filenames:
        print(args.message.format(filename))
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
