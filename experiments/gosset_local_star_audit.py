"""Exhaustive local-cell-star and global incidence report."""
from __future__ import annotations

import json

from gosset_local_star import audit_all_vertex_stars


def main() -> None:
    print(json.dumps(audit_all_vertex_stars(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
