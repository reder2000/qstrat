# asset example class
from abc import ABC, abstractmethod
from typing import Tuple

from pandas import Timestamp

Date = Timestamp


class Asset(ABC):
    @abstractmethod
    def price(self, t: Date) -> float:
        return 1.0

    def coupon(self, t: Date) -> float:
        return 0.0

    def __getitem__(self, t: Date) -> Tuple[float, float]:
        return [self.price(t), self.coupon(t)]

    def full_price(self, t: Date):
        return self.price(t) + self.coupon(t)

    def name(self) -> str:
        return None
