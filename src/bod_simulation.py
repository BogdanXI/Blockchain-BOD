"""Deterministic scenario runner for the BOD economic state machine."""
from dataclasses import dataclass
from typing import Tuple

from src.bod_economy import State, Transition, apply


@dataclass(frozen=True)
class StepResult:
    height: int
    minted: int
    burned: int
    supply: int
    unissued: int


def run(state: State, transitions: Tuple[Transition, ...]) -> tuple[State, Tuple[StepResult, ...]]:
    results = []
    current = state
    for transition in transitions:
        before_minted = current.minted
        before_burned = current.burned
        current = apply(current, transition)
        results.append(
            StepResult(
                height=current.height,
                minted=current.minted - before_minted,
                burned=current.burned - before_burned,
                supply=current.supply,
                unissued=current.unissued,
            )
        )
    return current, tuple(results)
