from abc import ABC, abstractmethod

class AbsCapSurface(ABC):

    @abstractmethod
    def interpolate_vol(self, expiry):
        pass
