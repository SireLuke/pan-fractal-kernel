"""Direct global Gosset 4-clique and local antipode audit."""
import json

from gosset_global_4cliques import audit_global_four_cliques, audit_local_antipodes


if __name__ == "__main__":
    print(json.dumps({
        "global_four_clique_audit": audit_global_four_cliques(),
        "local_antipode_audit": audit_local_antipodes(),
    }, indent=2, sort_keys=True))
