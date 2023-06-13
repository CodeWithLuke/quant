from abc import ABC, abstractmethod


class AbsInstrument(ABC):

    @property
    @abstractmethod
    def node_date(self):
        pass

    @property
    @abstractmethod
    def quote(self):
        pass

    @abstractmethod
    def calculate_zero_rate(self, partial_curve):
        pass