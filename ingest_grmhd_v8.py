#!/usr/bin/env python3
"""Download/read a GRMHD HDF5 dump, map sampled cells into V8, run JOBF.

Default source is the public Illinois v3 GRMHD SANE a*=+0.5 288x128x128
HARM dump. A single dump is about 144 MB; it is downloaded locally and is
not committed to Git. Use --input to supply another compatible HARM/KHARMA
HDF5 primitive dump.

Dependencies: numpy, h5py
Example:
  python ingest_grmhd_v8.py --max-cells 50000 --output grmhd_v8_jobf_test.csv
"""
from __future__ import annotations
import argparse, csv, urllib.request
from pathlib import Path
import h5py
import numpy as np
from v8_ingest_common import robust01, run_v8_jobf, V8_KEYS

DEFAULT_URL = ("https://thz.astro.illinois.edu/v3_grmhd/SANE/"
               "a%2B0.5/288x128x128/torus.out0.05000.h5")

def download(url, path):
    if path.exists() and path.stat().st_size:
        print(f"Using cached dump: {path}")
        return
    print(f"Downloading GRMHD snapshot: {url}")
    urllib.request.urlretrieve(url, path)
    if path.stat().st_size < 1024:
        raise RuntimeError("Downloaded file is unexpectedly small")

def find_primitive_dataset(h5, requested=None):
    candidates=[]
    def visit(name,obj):
        if isinstance(obj,h5py.Dataset) and obj.ndim==4:
            candidates.append((name,obj.shape))
    h5.visititems(visit)
    if requested:
        if requested not in h5: raise KeyError(f"No dataset {requested!r}")
        ds=h5[requested]
        if ds.ndim!=4: raise ValueError("Primitive dataset must be 4D")
        return requested, ds[...]
    for name,shape in candidates:
        if shape[0] in (8,9,10,11,12) or shape[-1] in (8,9,10,11,12):
            return name,h5[name][...]
    raise RuntimeError("Could not identify a 4D primitive array. Inspect HDF5 "
                       "and pass --primitive-key explicitly.")

def canonical_primitives(array):
    # HARM primitive ordering: rho, uu, u1,u2,u3,b1,b2,b3; tolerate
    # either variable-first or variable-last storage.
    if array.shape[0] in (8,9,10,11,12):
        a=np.moveaxis(array,0,-1)
    elif array.shape[-1] in (8,9,10,11,12):
        a=array
    else:
        raise ValueError(f"Unrecognized primitive-array shape {array.shape}")
    if a.shape[-1] < 8:
        raise ValueError("Need at least 8 HARM primitive variables")
    return [np.asarray(a[...,i],dtype=float) for i in range(8)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,default=Path("torus.out0.05000.h5"))
    p.add_argument("--url",default=DEFAULT_URL)
    p.add_argument("--primitive-key",default=None,
                   help="HDF5 path to 4D primitive array; auto-detected if omitted")
    p.add_argument("--max-cells",type=int,default=50000)
    p.add_argument("--steps",type=int,default=24)
    p.add_argument("--samples",type=int,default=256)
    p.add_argument("--dt",type=float,default=.01)
    p.add_argument("--shape-bias",type=float,default=0.0)
    p.add_argument("--output",default="grmhd_v8_jobf_test.csv")
    a=p.parse_args()
    download(a.url,a.input)
    with h5py.File(a.input,"r") as h5:
        key, raw=find_primitive_dataset(h5,a.primitive_key)
        rho,uu,u1,u2,u3,b1,b2,b3=canonical_primitives(raw)
        attrs={str(k):str(v) for k,v in h5.attrs.items()}
    flat=[x.reshape(-1) for x in (rho,uu,u1,u2,u3,b1,b2,b3)]
    ncell=flat[0].size
    stride=max(1,ncell//a.max_cells)
    idx=np.arange(0,ncell,stride,dtype=int)[:a.max_cells]
    r, e, v1,v2,v3, B1,B2,B3=[x[idx] for x in flat]
    finite=np.isfinite(r)&np.isfinite(e)&np.isfinite(v1)&np.isfinite(v2)&np.isfinite(v3)
    finite &= np.isfinite(B1)&np.isfinite(B2)&np.isfinite(B3)&(r>0)&(e>0)
    r,e,v1,v2,v3,B1,B2,B3=[x[finite] for x in (r,e,v1,v2,v3,B1,B2,B3)]
    if r.size<8: raise RuntimeError("Too few valid primitive cells after filtering")

    bmag=np.sqrt(B1*B1+B2*B2+B3*B3)
    vmag=np.sqrt(v1*v1+v2*v2+v3*v3)
    # Proxies only: preserve primitive values in each output row.
    # tau is snapshot-time placeholder (single-dump test); chi encodes
    # azimuthal velocity orientation from the local (v2,v3) plane.
    chi=(np.arctan2(v3,v2)+np.pi)/(2*np.pi)
    features=np.column_stack((
      robust01(1.0/(1.0+np.abs(np.log10(np.maximum(r,1e-30))))),
      robust01(np.log1p(np.arange(r.size,dtype=float))),
      robust01(np.log1p(np.maximum(e/r,0))),
      robust01(np.log1p(np.maximum(bmag*bmag/np.maximum(r,1e-30),0))),
      np.full(r.size,.5),
      chi,
      robust01(np.log1p(np.maximum(r,0))),
      robust01(np.log1p(np.maximum(bmag*vmag,0))),
    ))
    out=[]
    for i, vec in enumerate(features):
        record={
          "snapshot_file":a.input.name,"primitive_dataset":key,
          "cell_sample_index":int(idx[finite][i]),
          "rho":float(r[i]),"uu":float(e[i]),
          "u1":float(v1[i]),"u2":float(v2[i]),"u3":float(v3[i]),
          "b1":float(B1[i]),"b2":float(B2[i]),"b3":float(B3[i]),
          "magnetic_field_magnitude":float(bmag[i]),
          "velocity_magnitude":float(vmag[i]),
        }
        for name,val in zip(V8_KEYS,vec): record["v8_"+name+"_proxy"]=float(val)
        record.update(run_v8_jobf(vec,steps=a.steps,dt=a.dt,samples=a.samples,
                                   seed=23,shape_bias=a.shape_bias))
        out.append(record)
    with open(a.output,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(f"GRMHD primitive dump: {a.input}; dataset={key}")
    print(f"Valid sampled cells ingested into V8: {len(out)} / {ncell}")
    print(f"All JOBF boundaries positive: {all(x['jobf_boundary_positive'] for x in out)}")
    print(f"HDF5 root attrs: {attrs}")
    print(f"Wrote {a.output}")

if __name__=="__main__": main()
