"""Built-in ABOM-V8 plug-ins that wrap existing package-owned capabilities.

These are adapters, not copies of the underlying mathematical engines.
"""
from __future__ import annotations

from typing import Any

from .registry import PluginDescriptor, PluginRegistry
from ..diagnostics.cartesian import curl, divergence, gradient, laplacian
from ..occupancy.fermi import occupancy_profile
from ..occupancy.menger import (
    flux_from_asymmetry, lemniscate_flux, menger_hausdorff_dimension,
    menger_volume_fraction, mu_cube_volume,
)
from ..lattice.microtubule import MicrotubuleLattice
from ..transport.curves import CurveSamples, sample_bernoulli, sample_gerono
from ..transport.experiments import compare_lemniscates, resolution_sweep
from ..harmonics import log_phi_ratio, phi_power
from ..mu_cube import MuCube, MuCubeRegistry
from ..state import V8State
from ..trajectory import V8Trajectory
from ..visualization.radial_shells import golden_angle_shells
from menger_wave_coupling import menger_wave_coupling
from ..strata import (
    abom_strata_records, lemniscate_strata_record, menger_flux_strata_record,
    microtubule_interpretation_strata_record, microtubule_lattice_strata_record,
    model_routing_strata_record, provenance_strata_record,
)


class StrataEvidencePlugin:
    descriptor = PluginDescriptor(
        "abom.validation.strata-evidence", "0.1.0", ("0.1",),
        ("validation.strata-report", "validation.evidence-promotion-gate"),
    )

    create_lemniscate_record = staticmethod(lemniscate_strata_record)
    create_menger_flux_record = staticmethod(menger_flux_strata_record)
    create_microtubule_lattice_record = staticmethod(microtubule_lattice_strata_record)
    create_microtubule_interpretation_record = staticmethod(microtubule_interpretation_strata_record)
    create_model_routing_record = staticmethod(model_routing_strata_record)
    create_provenance_record = staticmethod(provenance_strata_record)
    all_records = staticmethod(abom_strata_records)


class LemniscateComparisonPlugin:
    descriptor = PluginDescriptor(
        "abom.experiment.lemniscate-comparison", "0.1.0", ("0.1",),
        ("experiment.curve-normalization", "experiment.resolution-sweep"),
    )

    compare = staticmethod(compare_lemniscates)
    resolution_sweep = staticmethod(resolution_sweep)


class GeronoCurvePlugin:
    descriptor = PluginDescriptor(
        "abom.transport.gerono", "0.1.0", ("0.1",),
        ("transport.lemniscate", "transport.bidirectional-candidate"),
    )

    def sample(self, *, a: float = 1.0, b: float = 0.5,
               n_samples: int = 401) -> CurveSamples:
        return sample_gerono(a=a, b=b, n_samples=n_samples)


class BernoulliCurvePlugin:
    descriptor = PluginDescriptor(
        "abom.transport.bernoulli", "0.1.0", ("0.1",),
        ("transport.lemniscate", "transport.comparison-candidate"),
    )

    def sample(self, *, c: float = 1.0, n_samples: int = 401) -> CurveSamples:
        return sample_bernoulli(c=c, n_samples=n_samples)


class FermiOccupancyPlugin:
    descriptor = PluginDescriptor(
        "abom.occupancy.fermi-dirac", "0.1.0", ("0.1",),
        ("occupancy.fermi-dirac", "occupancy.binary-entropy"),
    )

    def evaluate(self, *, energy: float, chemical_potential: float,
                 temperature: float):
        return occupancy_profile(energy, chemical_potential, temperature)


class CartesianFieldDiagnosticsPlugin:
    descriptor = PluginDescriptor(
        "abom.diagnostics.cartesian-3d", "0.1.0", ("0.1",),
        ("field.gradient", "field.divergence", "field.curl", "field.laplacian"),
    )

    gradient = staticmethod(gradient)
    divergence = staticmethod(divergence)
    curl = staticmethod(curl)
    laplacian = staticmethod(laplacian)


class MuCubeStatePlugin:
    descriptor = PluginDescriptor(
        "abom.state.mu-cube", "0.1.0", ("0.1",),
        ("state.mu-cube", "state.recursive-containment", "state.occupancy"),
    )

    def create(self, *, cell_id: str, state: V8State, occupancy: float,
               resonance: float = 0.5, scale: float = 1.0,
               recursion_level: int = 0, parent_id: str | None = None,
               connections: tuple[str, ...] = ()) -> MuCube:
        return MuCube(cell_id, state, occupancy, resonance, scale,
                      recursion_level, parent_id, connections)

    def registry(self) -> MuCubeRegistry:
        return MuCubeRegistry()


class V8TrajectoryPlugin:
    descriptor = PluginDescriptor(
        "abom.navigation.v8-trajectory", "0.1.0", ("0.1",),
        ("navigation.past-current-future", "navigation.snapshot-sequence"),
    )

    def create(self, frames: tuple[V8State, ...], current_index: int = 0) -> V8Trajectory:
        return V8Trajectory(frames, current_index)


class GoldenHarmonicScalePlugin:
    descriptor = PluginDescriptor(
        "abom.scale.golden-ratio", "0.1.0", ("0.1",),
        ("scale.phi-power", "scale.dimensionless-log-ratio"),
    )

    phi_power = staticmethod(phi_power)
    log_phi_ratio = staticmethod(log_phi_ratio)


class GoldenAngleShellVisualizationPlugin:
    descriptor = PluginDescriptor(
        "abom.visualization.golden-angle-shells", "0.1.0", ("0.1",),
        ("visualization.radial-shells", "visualization.phi-scaled"),
    )

    generate = staticmethod(golden_angle_shells)


class MengerGraphPlugin:
    """Optional adapter over the Fractal Kernel's existing Menger graph engine."""

    descriptor = PluginDescriptor(
        "kernel.geometry.menger-finite-graph", "0.1.0", ("0.1",),
        ("geometry.menger-sponge", "graph.face-adjacency"),
    )

    def build(self, *, dimension: int = 3, level: int = 1) -> dict[str, Any]:
        # Lazy import keeps this adapter boundary optional for consumers that
        # only use occupancy, curves or field diagnostics.
        from menger_sponge import adjacency, audit_menger, menger_cells

        cells = menger_cells(dimension, level)
        graph = adjacency(cells, 3**level)
        audit = audit_menger(dimension, level)
        return {"dimension": dimension, "level": level,
                "cells": cells, "adjacency": graph, "audit": audit}


class MengerMuCubePlugin:
    """Exact Menger volume/flux identities over occupancy (no physical claim)."""

    descriptor = PluginDescriptor(
        "abom.occupancy.menger-mu-cube", "0.1.0", ("0.1",),
        ("occupancy.menger-volume", "occupancy.two-state-flux",
         "geometry.similarity-dimension"),
    )

    volume_fraction = staticmethod(menger_volume_fraction)
    mu_cube_volume = staticmethod(mu_cube_volume)
    hausdorff_dimension = staticmethod(menger_hausdorff_dimension)
    flux = staticmethod(lemniscate_flux)
    flux_from_asymmetry = staticmethod(flux_from_asymmetry)


class MengerWaveCouplingPlugin:
    """Semi-transparent finite Menger mask applied to a complex scalar field."""

    descriptor = PluginDescriptor(
        "kernel.wave.menger-coupling", "0.1.0", ("0.1",),
        ("wavefield.complex-scalar", "geometry.menger-mask", "coupling.attenuation-phase"),
    )

    couple = staticmethod(menger_wave_coupling)


class MicrotubuleLatticePlugin:
    """Combinatorial 13_3 microtubule lattice geometry (nominal parameters)."""

    descriptor = PluginDescriptor(
        "abom.lattice.microtubule-13-3", "0.1.0", ("0.1",),
        ("lattice.helix-families", "lattice.seam", "lattice.wrap-unwrap"),
    )

    def create(self, *, n_protofilaments: int = 13, start: int = 3,
               monomer_nm: float = 4.0, radius_nm: float = 10.0) -> MicrotubuleLattice:
        return MicrotubuleLattice(n_protofilaments, start, monomer_nm, radius_nm)


def register_builtin_plugins(registry: PluginRegistry) -> dict[str, object]:
    """Register the stable v0.1 built-ins and return them by plug-in id."""
    plugins: tuple[object, ...] = (
        GeronoCurvePlugin(),
        StrataEvidencePlugin(),
        LemniscateComparisonPlugin(),
        BernoulliCurvePlugin(),
        FermiOccupancyPlugin(),
        CartesianFieldDiagnosticsPlugin(),
        MengerGraphPlugin(),
        MuCubeStatePlugin(),
        V8TrajectoryPlugin(),
        GoldenHarmonicScalePlugin(),
        GoldenAngleShellVisualizationPlugin(),
        MengerMuCubePlugin(),
        MengerWaveCouplingPlugin(),
        MicrotubuleLatticePlugin(),
    )
    registered: dict[str, object] = {}
    for plugin in plugins:
        descriptor = plugin.descriptor  # type: ignore[attr-defined]
        registry.register(plugin)  # type: ignore[arg-type]
        registered[descriptor.plugin_id] = plugin
    return registered
