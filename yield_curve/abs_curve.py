from abc import ABC, abstractmethod


class AbsCurve(ABC):

    @abstractmethod
    def interpolate_curve(self, t):
        pass

    @abstractmethod
    def interpolate_discount_factor(self, t):
        pass
