# Curve comparison protocol v0.1

Each curve implementation is normalized against declared comparison constraints, not assumed to share a natural radius parameter.

| Candidate | Definition | Configurable scale | Notes |
|---|---|---|---|
| Gerono | (x=a\cos t, y=b\sin(2t)) | independent (a,b) | Initial default; broad lobes are easy to configure |
| Bernoulli | (r^2=c^2\cos(2\theta)) | (c) | Classical lemniscate; real-domain handling required |
| Alternate lemniscates | implementation-specific | implementation-specific | Must declare parameter domain and invariants |

Required common comparison modes:
1. same bounding-box width;
2. same lobe area;
3. same total arc length (within declared numerical tolerance).

Report origin crossings, lobe area, bounding dimensions, arc length, curvature and sampling sensitivity.