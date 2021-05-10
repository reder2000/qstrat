# asset example class
from abc import ABC, abstractmethod
from typing import Tuple

from common import Date


class Asset(ABC):
    def __init__(self, name, maturity):
        self.name = name
        self.maturity = maturity or Date(2100, 12, 31)

    @abstractmethod
    def price(self, t: Date) -> float:
        raise NotImplementedError

    @abstractmethod
    def coupon(self, t: Date) -> float:
        raise NotImplementedError

    def __getitem__(self, t: Date) -> Tuple[float, float]:
        return [self.price(t), self.coupon(t)]

    def full_price(self, t: Date):
        return self.price(t) + self.coupon(t)

    def name(self) -> str:
        return None
