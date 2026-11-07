import json, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = json.load(open("production_results.json"))
fig, ax = plt.subplots(1, 3, figsize=(16, 5), dpi=150)
col = {"SU2_3D": "#1f77b4", "SU2_4D": "#d62728", "SU3_4D": "#2ca02c"}; lab = {"SU2_3D": "SU(2) 3D 12³", "SU2_4D": "SU(2) 4D 8⁴", "SU3_4D": "SU(3) 4D 8⁴"}
for k, v in R.items():
    b = [r["beta"] for r in v]
    ax[0].errorbar(b, [r["plaq"] for r in v], [r["plaq_err"] for r in v], fmt="o-", c=col[k], label=lab[k], capsize=2)
    ax[1].errorbar(b, [r["creutz2"] for r in v], [r["creutz2_err"] for r in v], fmt="o-", c=col[k], label=lab[k], capsize=2)
    ax[2].plot(b, [r["plaq"] - r["strong_ref"] for r in v], "o-", c=col[k], label=lab[k] + " − strong-coupling ref")
ax[0].set_title("Plaquette ⟨(1/N)ReTr U_p⟩ (MC, ±binned err)"); ax[0].set_xlabel("β"); ax[0].legend()
ax[1].set_title("Creutz ratio χ(2,2)"); ax[1].set_xlabel("β"); ax[1].set_yscale("log"); ax[1].legend()
ax[2].set_title("MC − strong-coupling reference\n(SU(2): I₂/I₁ leading term; SU(3): 1408.2960 series)\nvalid only at small β"); ax[2].set_xlabel("β"); ax[2].axhline(0, c="k", lw=.5); ax[2].legend()
fig.text(.5, .005, "Toy validation. Errors: 20-bin blocking, autocorrelation not estimated. Not a physical-QCD claim; no finite-size or continuum extrapolation.", ha="center", fontsize=8)
plt.tight_layout(rect=(0, .03, 1, 1)); plt.savefig("Lattice_Gauge_Validation.png")
