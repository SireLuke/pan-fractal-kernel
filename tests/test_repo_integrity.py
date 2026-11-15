"""Guards against broken merges: duplicate definitions, workflow YAML, scan CLI flags."""
import collections
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_no_duplicate_top_level_definitions_in_scan_runner():
    text = (ROOT / "run_wilson_flow_sector_scan.py").read_text(encoding="utf-8")
    names = re.findall(r"^(?:def|class) (\w+)", text, re.M)
    assert [n for n, c in collections.Counter(names).items() if c > 1] == []


def test_scan_cli_exposes_all_documented_flags():
    out = subprocess.run([sys.executable, str(ROOT / "run_wilson_flow_sector_scan.py"), "-h"],
                         capture_output=True, text=True, check=True, cwd=ROOT).stdout
    for flag in ("--extent", "--steps", "--step-size", "--integrator", "--start", "--therm",
                 "--sep", "--configs", "--groups", "--beta", "--seeds", "--output"):
        assert flag in out, flag


def test_workflows_have_no_duplicate_yaml_keys():
    yaml = pytest.importorskip("yaml")

    class Loader(yaml.SafeLoader):
        pass

    def construct(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            assert key not in seen, f"duplicate key {key!r} at line {key_node.start_mark.line + 1}"
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct)
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        yaml.load(wf.read_text(encoding="utf-8"), Loader)
