from abc import ABC, abstractmethod


class AbsSwaptionSurface(ABC):

    @abstractmethod
    def interpolate_vol(self, expiry, tenor):
        pass

    @abstractmethod
    def bump_surface(self, n_bps_bump=1):
        pass
