"""Transparent leading-order QCD reference calculations.

Pedagogical benchmark only; fixed N_f must not be used across heavy-quark
thresholds without a matching prescription.
"""
import math


def beta0(nc=3, nf=5):
    if isinstance(nc, bool) or isinstance(nf, bool) or nc <= 0 or nf < 0:
        raise ValueError("nc must be positive and nf non-negative")
    return float(11 * nc - 2 * nf)


def beta_alpha_s(alpha_s, *, nc=3, nf=5):
    if not math.isfinite(alpha_s) or alpha_s <= 0:
        raise ValueError("alpha_s must be finite and positive")
    return -(beta0(nc, nf) * alpha_s**2) / (12.0 * math.pi)


def alpha_s_one_loop(mu_gev, lambda_qcd_gev, *, nc=3, nf=5):
    if not math.isfinite(mu_gev) or not math.isfinite(lambda_qcd_gev):
        raise ValueError("mu and Lambda_QCD must be finite")
    if mu_gev <= 0 or lambda_qcd_gev <= 0 or mu_gev <= lambda_qcd_gev:
        raise ValueError("Require mu > Lambda_QCD > 0")
    b0 = beta0(nc, nf)
    if b0 <= 0:
        raise ValueError("This parameter choice is not asymptotically free")
    return 12.0 * math.pi / (b0 * math.log((mu_gev / lambda_qcd_gev) ** 2))


def lambda_from_reference(mu_ref_gev, alpha_ref, *, nc=3, nf=5):
    if not math.isfinite(mu_ref_gev) or mu_ref_gev <= 0:
        raise ValueError("reference scale must be finite and positive")
    if not math.isfinite(alpha_ref) or alpha_ref <= 0:
        raise ValueError("reference alpha_s must be finite and positive")
    b0 = beta0(nc, nf)
    if b0 <= 0:
        raise ValueError("This parameter choice is not asymptotically free")
    return mu_ref_gev * math.exp(-6.0 * math.pi / (b0 * alpha_ref))


def asymptotically_free(nc=3, nf=5):
    return beta0(nc, nf) > 0
