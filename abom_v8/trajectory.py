"""Small immutable navigator for ordered V8 snapshots.

Frame order is supplied by the caller. It is not inferred from tau, and stepping
through frames is not a physical time-evolution solver.
"""
from __future__ import annotations

from dataclasses import dataclass

from .state import V8State


@dataclass(frozen=True, slots=True)
class V8Trajectory:
    frames: tuple[V8State, ...]
    current_index: int = 0

    def __post_init__(self) -> None:
        frames = tuple(self.frames)
        if not frames or any(not isinstance(frame, V8State) for frame in frames):
            raise ValueError("trajectory requires at least one validated V8State frame")
        if isinstance(self.current_index, bool) or not isinstance(self.current_index, int):
            raise ValueError("current_index must be an integer")
        if not 0 <= self.current_index < len(frames):
            raise IndexError("current_index is outside the trajectory")
        object.__setattr__(self, "frames", frames)

    @property
    def current(self) -> V8State:
        return self.frames[self.current_index]

    @property
    def past(self) -> tuple[V8State, ...]:
        return self.frames[:self.current_index]

    @property
    def future(self) -> tuple[V8State, ...]:
        return self.frames[self.current_index + 1:]

    def seek(self, index: int) -> "V8Trajectory":
        return V8Trajectory(self.frames, index)

    def step(self, offset: int) -> "V8Trajectory":
        if isinstance(offset, bool) or not isinstance(offset, int):
            raise ValueError("offset must be an integer")
        return self.seek(self.current_index + offset)
