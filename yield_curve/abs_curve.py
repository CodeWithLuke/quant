from abc import ABC, abstractmethod
from math import log

from utils.enum import InterestType


class AbsCurve(ABC):

    @abstractmethod
    def interpolate_curve(self, t):
        pass

    @abstractmethod
    def interpolate_discount_factor(self, t, compounding=InterestType.CONTINUOUS):
        pass

    @abstractmethod
    def bump_curve_by_instrument(self, n_bps_bump=1):
        pass

    @abstractmethod
    def parallel_bump_curve(self, n_bps_bump=1):
        pass

    def interpolate_forward_rate(self, t, term=1):
        t_a = t
        t_b = t + term

        d_a = self.interpolate_discount_factor(t_a, compounding=InterestType.CONTINUOUS)

        d_b = self.interpolate_discount_factor(t_b, compounding=InterestType.CONTINUOUS)

        return -1 * log(d_b / d_a) / term