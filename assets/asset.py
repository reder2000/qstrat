# asset example class
from abc import ABC, abstractmethod
from typing import Tuple

from pandas import Timestamp

Date = Timestamp


class Asset(ABC):
    def __init__(self, name):
        self.name = name

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
