#!/usr/bin/env python3
"""Fetch Gaia DR3 sources, map declared proxies into V8, and run JOBF.

Example:
  python ingest_gaia_v8.py --rows 256 --output gaia_v8_jobf_test.csv

The V8 values are engineering proxies, not direct Gaia measurements of
PAN V8 semantics. Original Gaia fields and source_id are retained per row.
"""
from __future__ import annotations
import argparse, csv, io, math, urllib.parse, urllib.request
import numpy as np
from v8_ingest_common import robust01, run_v8_jobf, V8_KEYS

TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
QUERY = """
SELECT TOP {n} source_id, ra, dec, parallax, parallax_error,
 parallax_over_error, pmra, pmdec, phot_g_mean_mag, bp_rp, ruwe,
 astrometric_excess_noise, astrometric_excess_noise_sig,
 astrometric_n_obs_al, phot_g_mean_flux_over_error
FROM gaiadr3.gaia_source
WHERE parallax_over_error > 5 AND pmra IS NOT NULL AND pmdec IS NOT NULL
 AND ruwe < 1.4 AND phot_g_mean_mag < 15
 AND astrometric_excess_noise IS NOT NULL
 AND astrometric_excess_noise_sig IS NOT NULL
 AND astrometric_n_obs_al IS NOT NULL
 AND phot_g_mean_flux_over_error IS NOT NULL
ORDER BY random_index
"""

def fetch(n):
    body = urllib.parse.urlencode({
        "REQUEST":"doQuery", "LANG":"ADQL", "FORMAT":"csv",
        "QUERY":QUERY.format(n=n).strip()
    }).encode()
    req = urllib.request.Request(TAP, data=body,
        headers={"Content-Type":"application/x-www-form-urlencoded",
                 "User-Agent":"PAN-V8-Gaia-ingest/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read().decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(data)))
    if not rows or "source_id" not in rows[0]:
        raise RuntimeError("Gaia TAP returned no usable source rows")
    return rows

def col(rows, name):
    return np.array([float(r[name]) for r in rows], dtype=float)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rows",type=int,default=256)
    p.add_argument("--steps",type=int,default=24)
    p.add_argument("--samples",type=int,default=256)
    p.add_argument("--dt",type=float,default=.01)
    p.add_argument("--shape-bias",type=float,default=0.0)
    p.add_argument("--output",default="gaia_v8_jobf_test.csv")
    a=p.parse_args()
    rows=fetch(a.rows)
    ruwe=col(rows,"ruwe")
    pm=np.hypot(col(rows,"pmra"),col(rows,"pmdec"))
    parallax_snr=col(rows,"parallax_over_error")
    excess=col(rows,"astrometric_excess_noise")
    excess_sig=col(rows,"astrometric_excess_noise_sig")
    nobs=col(rows,"astrometric_n_obs_al")
    flux_snr=col(rows,"phot_g_mean_flux_over_error")
    proxies=np.column_stack((
      np.clip(1-np.maximum(ruwe-1,0)/.4,0,1),
      robust01(np.log1p(np.maximum(parallax_snr,0))),
      robust01(np.log1p(np.maximum(pm,0))),
      robust01(np.log1p(np.maximum(excess,0))),
      robust01(nobs),
      (np.arctan2(col(rows,"pmdec"),col(rows,"pmra"))+np.pi)/(2*np.pi),
      robust01(np.log1p(np.maximum(flux_snr,0))),
      robust01(np.log1p(np.maximum(excess_sig,0))),
    ))
    out=[]
    for i, source in enumerate(rows):
        record=dict(source)
        for key,val in zip(V8_KEYS,proxies[i]): record["v8_"+key+"_proxy"]=float(val)
        record.update(run_v8_jobf(proxies[i],steps=a.steps,dt=a.dt,
                                  samples=a.samples,seed=17,shape_bias=a.shape_bias))
        out.append(record)
    with open(a.output,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f"Gaia DR3 rows ingested into V8: {len(out)}")
    print(f"All JOBF boundaries positive: {all(x['jobf_boundary_positive'] for x in out)}")
    print(f"Wrote {a.output}")

if __name__=="__main__": main()
