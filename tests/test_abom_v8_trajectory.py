import pytest

from abom_v8.state import V8State
from abom_v8.trajectory import V8Trajectory


def frame(value):
    return V8State.from_sequence([value] * 8)


def test_past_current_future_and_seek():
    trajectory = V8Trajectory((frame(0.1), frame(0.5), frame(0.9)), current_index=1)
    assert len(trajectory.past) == 1
    assert trajectory.current.coordinates[0] == pytest.approx(0.5)
    assert len(trajectory.future) == 1
    moved = trajectory.seek(2)
    assert moved.current.coordinates[0] == pytest.approx(0.9)
    assert trajectory.current.coordinates[0] == pytest.approx(0.5)


def test_step_and_bounds():
    trajectory = V8Trajectory((frame(0.1), frame(0.5), frame(0.9)))
    assert trajectory.step(1).current.coordinates[0] == pytest.approx(0.5)
    with pytest.raises(IndexError):
        trajectory.step(3)
    with pytest.raises(ValueError):
        trajectory.step(0.5)


def test_rejects_empty_or_untyped_trajectory():
    with pytest.raises(ValueError):
        V8Trajectory(())
    with pytest.raises(ValueError):
        V8Trajectory((object(),))
