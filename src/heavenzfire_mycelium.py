"""Deterministic multidimensional pixel-mycelium lattice engine.

This is a computational model, not a biological mycelium claim. It stores a real
N-dimensional scalar field, derives orthogonal neighbor edges, and performs bounded
weighted diffusion/decay updates. The rendering/export layer is intentionally separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import prod
from typing import Iterable, Sequence


Coordinate = tuple[int, ...]


@dataclass(frozen=True)
class LatticeConfig:
    shape: tuple[int, ...]
    diffusion: float = 0.2
    decay: float = 0.0
    wrap_edges: bool = False

    def validate(self) -> None:
        if not self.shape or len(self.shape) > 8:
            raise ValueError("shape must have between 1 and 8 dimensions")
        if any(not isinstance(n, int) or n < 1 for n in self.shape):
            raise ValueError("each shape dimension must be a positive integer")
        if not 0.0 <= self.diffusion <= 1.0:
            raise ValueError("diffusion must be between 0 and 1")
        if not 0.0 <= self.decay <= 1.0:
            raise ValueError("decay must be between 0 and 1")


class PixelMycelium:
    """N-dimensional lattice with explicit neighbor topology and deterministic updates."""

    def __init__(self, config: LatticeConfig, initial: float = 0.0) -> None:
        config.validate()
        if not 0.0 <= initial <= 1.0:
            raise ValueError("initial value must be between 0 and 1")
        self.config = config
        self._values: dict[Coordinate, float] = {
            coordinate: float(initial) for coordinate in self.coordinates()
        }
        self.steps = 0

    @property
    def dimensions(self) -> int:
        return len(self.config.shape)

    @property
    def cell_count(self) -> int:
        return prod(self.config.shape)

    def coordinates(self) -> Iterable[Coordinate]:
        return product(*(range(size) for size in self.config.shape))

    def _validate_coordinate(self, coordinate: Sequence[int]) -> Coordinate:
        point = tuple(coordinate)
        if len(point) != self.dimensions:
            raise ValueError(f"coordinate must have {self.dimensions} dimensions")
        if any(not isinstance(v, int) or v < 0 or v >= self.config.shape[i]
               for i, v in enumerate(point)):
            raise IndexError(f"coordinate out of bounds: {point}")
        return point

    def get(self, coordinate: Sequence[int]) -> float:
        return self._values[self._validate_coordinate(coordinate)]

    def set(self, coordinate: Sequence[int], value: float) -> None:
        point = self._validate_coordinate(coordinate)
        if not 0.0 <= value <= 1.0:
            raise ValueError("cell value must be between 0 and 1")
        self._values[point] = float(value)

    def neighbors(self, coordinate: Sequence[int]) -> tuple[Coordinate, ...]:
        point = self._validate_coordinate(coordinate)
        found: set[Coordinate] = set()
        for axis in range(self.dimensions):
            for delta in (-1, 1):
                candidate = list(point)
                candidate[axis] += delta
                if self.config.wrap_edges:
                    candidate[axis] %= self.config.shape[axis]
                elif not 0 <= candidate[axis] < self.config.shape[axis]:
                    continue
                found.add(tuple(candidate))
        found.discard(point)
        return tuple(sorted(found))

    def activate(self, coordinate: Sequence[int], amount: float = 1.0) -> None:
        point = self._validate_coordinate(coordinate)
        if not 0.0 <= amount <= 1.0:
            raise ValueError("activation must be between 0 and 1")
        self._values[point] = max(self._values[point], float(amount))

    def step(self, iterations: int = 1) -> None:
        if not isinstance(iterations, int) or iterations < 0:
            raise ValueError("iterations must be a nonnegative integer")
        for _ in range(iterations):
            previous = self._values
            updated: dict[Coordinate, float] = {}
            for point, value in previous.items():
                adjacent = self.neighbors(point)
                if adjacent:
                    mean_neighbor = sum(previous[n] for n in adjacent) / len(adjacent)
                    mixed = value * (1.0 - self.config.diffusion) + mean_neighbor * self.config.diffusion
                else:
                    mixed = value
                updated[point] = min(1.0, max(0.0, mixed * (1.0 - self.config.decay)))
            self._values = updated
            self.steps += 1

    def slice_2d(self, fixed: Sequence[int] | None = None) -> list[list[float]]:
        """Return a 2D pixel slice; remaining dimensions are fixed to supplied indices."""
        if self.dimensions < 2:
            raise ValueError("a 2D slice requires at least two dimensions")
        fixed = tuple(fixed or (0,) * (self.dimensions - 2))
        if len(fixed) != self.dimensions - 2:
            raise ValueError(f"provide {self.dimensions - 2} fixed indices")
        for axis, index in enumerate(fixed):
            if not isinstance(index, int) or index < 0 or index >= self.config.shape[axis]:
                raise IndexError(f"fixed index out of bounds for axis {axis}: {index}")
        height, width = self.config.shape[-2:]
        prefix = fixed
        return [
            [self._values[prefix + (y, x)] for x in range(width)]
            for y in range(height)
        ]

    def summary(self) -> dict[str, int | float | tuple[int, ...]]:
        values = tuple(self._values.values())
        return {
            "shape": self.config.shape,
            "dimensions": self.dimensions,
            "cells": self.cell_count,
            "steps": self.steps,
            "active_cells": sum(value > 0.0 for value in values),
            "minimum": min(values),
            "maximum": max(values),
            "mean": sum(values) / len(values),
        }
