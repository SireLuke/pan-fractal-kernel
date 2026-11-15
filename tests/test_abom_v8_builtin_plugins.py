import numpy as np
import pytest

from abom_v8.adapters.builtins import (
    BernoulliCurvePlugin, CartesianFieldDiagnosticsPlugin, FermiOccupancyPlugin,
    GeronoCurvePlugin, GoldenAngleShellVisualizationPlugin, GoldenHarmonicScalePlugin, LemniscateComparisonPlugin, MengerGraphPlugin, StrataEvidencePlugin,
    MuCubeStatePlugin, V8TrajectoryPlugin, MengerMuCubePlugin, MicrotubuleLatticePlugin,
    register_builtin_plugins,
)
from abom_v8.adapters.registry import PluginRegistry
from abom_v8.state import V8State


def test_builtin_plugins_register_as_optional_capabilities():
    registry = PluginRegistry()
    plugins = register_builtin_plugins(registry)
    assert len(plugins) == 13
    assert "abom.validation.strata-evidence" in plugins
    assert "abom.experiment.lemniscate-comparison" in plugins
    assert "abom.visualization.golden-angle-shells" in plugins
    assert "abom.state.mu-cube" in plugins
    assert "abom.navigation.v8-trajectory" in plugins
    assert "abom.scale.golden-ratio" in plugins
    assert registry.resolve("abom.occupancy.menger-mu-cube", schema_version="0.1") is plugins["abom.occupancy.menger-mu-cube"]
    assert registry.resolve("abom.lattice.microtubule-13-3", schema_version="0.1") is plugins["abom.lattice.microtubule-13-3"]
    assert registry.resolve("abom.transport.gerono", schema_version="0.1") is plugins["abom.transport.gerono"]
    assert registry.resolve("kernel.geometry.menger-finite-graph", schema_version="0.1") is plugins["kernel.geometry.menger-finite-graph"]
    assert registry.resolve("abom.state.mu-cube", schema_version="0.1") is plugins["abom.state.mu-cube"]
    assert registry.resolve("abom.navigation.v8-trajectory", schema_version="0.1") is plugins["abom.navigation.v8-trajectory"]
    assert registry.resolve("abom.scale.golden-ratio", schema_version="0.1") is plugins["abom.scale.golden-ratio"]


def test_gerono_and_bernoulli_adapters_return_curve_contract():
    gerono = GeronoCurvePlugin().sample(a=2.0, b=0.7)
    bernoulli = BernoulliCurvePlugin().sample(c=1.0)
    assert gerono.name == "gerono"
    assert bernoulli.name == "bernoulli"
    assert gerono.points.shape == bernoulli.points.shape


def test_occupancy_adapter_returns_complement_and_entropy():
    result = FermiOccupancyPlugin().evaluate(
        energy=0.0, chemical_potential=0.0, temperature=1.0
    )
    assert result.occupied == pytest.approx(0.5)
    assert result.unoccupied == pytest.approx(0.5)
    assert result.entropy_bits == pytest.approx(1.0)


def test_cartesian_diagnostic_adapter_uses_field_operator_contract():
    axis = np.linspace(-1.0, 1.0, 5)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    vector = np.stack((x, y, z))
    result = CartesianFieldDiagnosticsPlugin.divergence(vector, axis[1] - axis[0])
    assert np.allclose(result, 3.0)


def test_menger_adapter_wraps_existing_kernel_graph_engine():
    result = MengerGraphPlugin().build(dimension=3, level=1)
    assert result["cells"].shape == (20, 3)
    assert result["adjacency"].shape == (20, 20)
    assert result["audit"]["connected_components"] == 1


def test_mu_cube_trajectory_and_harmonic_adapters():
    state = V8State.from_sequence([0.5] * 8)
    cell = MuCubeStatePlugin().create(cell_id="cell-0", state=state, occupancy=0.5)
    assert cell.entropy_bits == pytest.approx(1.0)

    trajectory = V8TrajectoryPlugin().create((state, state), current_index=1)
    assert trajectory.current == state
    assert len(trajectory.past) == 1

    harmonic = GoldenHarmonicScalePlugin()
    assert harmonic.phi_power(2) == pytest.approx(2.6180339887)
    assert harmonic.log_phi_ratio(harmonic.phi_power(2), 1.0) == pytest.approx(2.0)

    strata = StrataEvidencePlugin.create_lemniscate_record()
    assert strata.promotion_eligible() is False

    comparison = LemniscateComparisonPlugin.compare(n_samples=101)
    assert "same_bounding_width" in comparison["comparisons"]

    shells = GoldenAngleShellVisualizationPlugin.generate(shell_count=3, points_per_shell=8)
    assert shells.shape == (3, 8, 2)


def test_menger_mu_cube_and_microtubule_adapters():
    menger = MengerMuCubePlugin
    assert menger.volume_fraction(2) == pytest.approx((20 / 27) ** 2)
    assert menger.flux(0.5) == pytest.approx(0.25)
    assert menger.flux_from_asymmetry(0.0) == pytest.approx(0.25)
    assert menger.hausdorff_dimension(3) == pytest.approx(2.7268, abs=1e-4)

    lattice = MicrotubuleLatticePlugin().create()
    assert lattice.seam_vector == (13, -3)
    assert lattice.families_are_fibonacci_closed() is True
