import json, time, sys
from lattice_gauge import *
cfg = [("SU2_3D", 2, (12,12,12), [1.0,2.0,3.0,4.0,6.0]), ("SU2_4D", 2, (8,8,8,8), [1.0,2.0,2.3,2.5,3.0,4.0]), ("SU3_4D", 3, (8,8,8,8), [4.0,5.0,5.7,6.0,6.5,7.0])]
out = {}
for name, N, dims, betas in cfg:
    out[name] = []
    for b in betas:
        t0 = time.time(); g, P, C = run(N, dims, b, 200, 400, seed=int(b*100), creutz_r=(2,), hits=2)
        cm, ce = creutz_binned(C[2]); d = len(dims)
        rec = dict(beta=b, plaq=float(P.mean()), plaq_err=binned_err(P), creutz2=cm, creutz2_err=ce, weak_lead=weak_coupling_leading(N, d, b), secs=round(time.time()-t0,1))
        rec["strong_ref"] = u_su2(b) if N == 2 else su3_strong_plaquette(b)
        out[name].append(rec); print(name, rec, flush=True)
        json.dump(out, open("production_results.json", "w"), indent=1)
print("DONE")
