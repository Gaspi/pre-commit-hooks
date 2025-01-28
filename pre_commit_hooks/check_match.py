#!/usr/bin/env python3

import argparse, re

from pre_commit_hooks.utils import CalledProcessError, cmd_output

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--regex',
        type=str,
        dest='regex',
        help='Fails if any staged files matches the given regex')
    parser.add_argument(
        '--message',
        type=str,
        dest='message',
        help='Warning message to emit',
        default="""You are trying to push modifications to a protected file: {}.
        If everything else looks fine and you know what you are doing, use `--no-verify` to skip all checks.""")
    args = parser.parse_args(argv)
    reg = re.compile(args.regex)
    all_valid = True
    try:
        for staged_file in cmd_output('git', 'diff', '--staged', '--name-only').splitlines():
            if reg.match(staged_file):
                all_valid = False
                print(args.message.format(staged_file))
    except CalledProcessError:
        print("Command failed: `git diff --staged --name-only`")
        return 1
    return 0 if all_valid else 1

if __name__ == "__main__":
    raise SystemExit(main())
