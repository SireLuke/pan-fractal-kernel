"""NAHT-LG-001 gate: lattice core must not depend on any PAN module."""
import ast, pathlib, sys
ALLOWED = {"numpy", "scipy", "fractions", "sys", "pathlib", "itertools", "json", "time"}
def test_core_imports_only_allowed():
    src = (pathlib.Path(__file__).resolve().parents[1] / "lattice_gauge.py").read_text()
    mods = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import): mods |= {a.name.split(".")[0] for a in n.names}
        if isinstance(n, ast.ImportFrom) and n.module: mods.add(n.module.split(".")[0])
    assert mods <= ALLOWED, f"unexpected imports: {mods - ALLOWED}"
if __name__ == "__main__":
    test_core_imports_only_allowed(); print("ok   test_core_imports_only_allowed")
