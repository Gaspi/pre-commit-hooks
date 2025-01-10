#!/usr/bin/env python3

import argparse
import re
from packaging.version import Version

from collections.abc import Sequence

from pre_commit_hooks.utils import CalledProcessError, cmd_output

from pathlib import Path

_memo = {}
def is_version_unbumped_chart_folder(path: Path | str) -> bool:
    """
    Check if given path correspond to a chart folder with not staged version bump for the Chart.yaml.
    """
    if path not in _memo:
        chart_yaml = path / "Chart.yaml"
        if not chart_yaml.exists():
            _memo[path] = False
        else:
            try:
                diff = cmd_output("git", "diff", "--staged", str(chart_yaml))
                old_version = re.search(r'\n\-version:\s*([0-9\.]+)\s*\n', diff)
                new_version = re.search(r'\n\+version:\s*([0-9\.]+)\s*\n', diff)
                _memo[path] = not old_version or not new_version or Version(new_version.group(1)) <= Version(old_version.group(1))
            except Exception:
                _memo[path] = False
        print("Memo",path,_memo[path])
    return _memo[path]

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b', '--branch', action='append',
        help='Restrict check to this branch',
    )
    args = parser.parse_args(argv)
    print("Branch:", args.branch)

    try:
        # If the hook is restricted to some (other) branches, return
        if args.branch and cmd_output("git", "rev-parse", "--abbrev-ref", "HEAD").strip() not in args.branch:
            return 0
        # Else retrieve all staged files
        changed_files = set(Path(f) for f in cmd_output('git', 'diff', '-staged', '--name-only').splitlines())
    except CalledProcessError:
        return 0
    print("changed_files:", changed_files)
    
    files_in_unbumped_charts = [
        file
        for file in changed_files
        if any(is_version_unbumped_chart_folder(folder) for folder in file.parents)
    ]
    print("files_in_unbumped_charts:", files_in_unbumped_charts)
    for file in files_in_unbumped_charts:
        print("File {} has staged modification but there is no bump in its helm chart version".format(file))
    return int(bool(files_in_unbumped_charts))

if __name__ == "__main__":
    raise SystemExit(main())
