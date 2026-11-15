import pytest

from abom_v8.mu_cube import MuCube, MuCubeRegistry
from abom_v8.state import V8State


def state(value=0.5):
    return V8State.from_sequence([value] * 8)


def test_mu_cube_occupancy_entropy_and_schema():
    cell = MuCube("root", state(), occupancy=0.5, resonance=0.75, scale=1.0)
    assert cell.entropy_bits == pytest.approx(1.0)
    schema = cell.as_schema()
    assert schema["cell_id"] == "root"
    assert schema["entropy_bits"] == pytest.approx(1.0)
    assert schema["state"]["coordinate_order"][4] == "tau"


def test_registry_validates_parent_and_symmetric_connections():
    registry = MuCubeRegistry()
    registry.register(MuCube("root", state(), occupancy=0.5))
    registry.register(MuCube("child-a", state(0.6), occupancy=0.75,
                             parent_id="root", recursion_level=1,
                             connections=("child-b",)))
    registry.register(MuCube("child-b", state(0.4), occupancy=0.25,
                             parent_id="root", recursion_level=1,
                             connections=("child-a",)))
    registry.validate_links(require_symmetric=True)
    assert [child.cell_id for child in registry.children_of("root")] == ["child-a", "child-b"]


def test_registry_rejects_duplicate_ids_and_dangling_links():
    registry = MuCubeRegistry()
    registry.register(MuCube("root", state(), occupancy=0.5))
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(MuCube("root", state(), occupancy=0.5))
    registry.register(MuCube("broken", state(), occupancy=0.5, connections=("missing",)))
    with pytest.raises(ValueError, match="unknown connection"):
        registry.validate_links()


def test_registry_rejects_parent_cycles():
    registry = MuCubeRegistry()
    registry.register(MuCube("a", state(), occupancy=0.5, parent_id="b", recursion_level=1))
    registry.register(MuCube("b", state(), occupancy=0.5, parent_id="a", recursion_level=1))
    with pytest.raises(ValueError, match="cycle"):
        registry.validate_links()


def test_registry_requires_child_recursion_level_to_increase():
    registry = MuCubeRegistry()
    registry.register(MuCube("root", state(), occupancy=0.5, recursion_level=1))
    registry.register(MuCube("child", state(), occupancy=0.5, parent_id="root", recursion_level=1))
    with pytest.raises(ValueError, match="greater recursion_level"):
        registry.validate_links()


def test_mu_cube_rejects_invalid_measure_and_self_connection():
    with pytest.raises(ValueError):
        MuCube("bad", state(), occupancy=1.2)
    with pytest.raises(ValueError):
        MuCube("self", state(), occupancy=0.5, connections=("self",))
