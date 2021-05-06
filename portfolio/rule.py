# compute new position from old one
from abc import ABC, abstractmethod
from typing import Tuple

from portfolio.position import Position
from common import Date


class Rule(ABC):
    @abstractmethod
    def new_position(
        self, at_date: Date, pv: float, previous_position: Position
    ) -> Tuple[Position, float, float]:
        pass

    # may be overridden
    def initial_position(
        self, at_date: Date, pv: float
    ) -> Tuple[Position, float, float]:
        return self.new_position(at_date, pv, None)
