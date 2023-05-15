from abc import ABC, abstractmethod

from datetime import date

from utils.enum import DayCountConvention


class AbsDayCountCalculator(ABC):

    @staticmethod
    @abstractmethod
    def day_count_convention() -> DayCountConvention:
        pass

    @staticmethod
    @abstractmethod
    def day_count(start_date: date, end_date: date) -> int:
        pass

    @staticmethod
    @abstractmethod
    def year_fraction(start_date: date, end_date: date) -> float:
        pass
