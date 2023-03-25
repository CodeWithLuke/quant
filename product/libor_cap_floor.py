from math import log, sqrt

from scipy.stats import norm

from product.libor_swap import LiborSwap
from utils.enum import CapFloor, LongShort, CashFlowFrequency
from vol_surface.cap_vol_surface import CapVolSurface
from yield_curve.libor_curve import LiborCurve


class Cap:

    def __init__(self, notional: float, strike_rate: float, maturity: float,
                 payment_frequency: CashFlowFrequency = CashFlowFrequency.SEMI_ANNUAL,
                 cap_floor: CapFloor = CapFloor.CAP, long_short: LongShort = LongShort.LONG):

        self._notional = notional

        self._strike_rate = strike_rate

        self._cap_floor = cap_floor

        self._long_short = long_short

        self._maturity = maturity

        assert round(12 * maturity) % payment_frequency == 0, maturity

        # time between reset date and payoff date
        self._period = 1 / payment_frequency

        self._reset_dates = []
        i = 1

        while round(self._period * i) < self._maturity:
            self._reset_dates.append(self._period * i)

            i += 1

        self._caplets = []

        for reset_date in self._reset_dates:
            self._caplets.append(self.build_caplet(reset_date))

    @classmethod
    def get_par_cap(cls, libor_curve: LiborCurve, notional: float, maturity: float,
                    payment_frequency: CashFlowFrequency, cap_floor: CapFloor = CapFloor.CAP,
                    long_short: LongShort = LongShort.LONG):
        strike_rate = cls._calc_par_rate(notional, maturity, libor_curve, payment_frequency)

        return cls(notional, strike_rate, maturity, payment_frequency, cap_floor, long_short)

    def build_caplet(self, reset_date: float):
        payoff_date = reset_date + self._period
        return Caplet(notional=self._notional, strike_rate=self._strike_rate, reset_date=reset_date,
                      payoff_date=payoff_date, cap_floor=self._cap_floor, long_short=self._long_short)

    def present_value(self, libor_curve: LiborCurve, vol_surface: CapVolSurface):

        volatility = vol_surface.interpolate_vol(self._maturity)

        pv = 0

        for caplet in self._caplets:
            pv += caplet.present_value(libor_curve, volatility)

        return pv

    @staticmethod
    def _calc_par_rate(notional: float, maturity: float, libor_curve: LiborCurve, payment_frequency: CashFlowFrequency):
        assert round(12 * maturity) % payment_frequency == 0, maturity
        swap_start = 1 / payment_frequency
        par_swap = LiborSwap.par_swap(libor_curve, notional, maturity - swap_start, payment_frequency,
                                      start_time=swap_start)
        return par_swap.swap_rate


class Caplet:

    def __init__(self, notional: float, strike_rate: float, reset_date: float, payoff_date: float,
                 cap_floor: CapFloor = CapFloor.CAP, long_short: LongShort = LongShort.LONG):
        self._notional = notional

        self._strike_rate = strike_rate

        self._reset_date = reset_date

        self._payoff_date = payoff_date

        self._period = payoff_date - reset_date

        self._cap_floor = cap_floor

        self._long_short = long_short

    def present_value(self, libor_curve: LiborCurve, volatility: float):
        forward_rate = libor_curve.interpolate_forward_rate(self._reset_date, self._period)

        notional_product = self._notional * self._period * libor_curve.interpolate_discount_factor(self._payoff_date)

        notional_product *= (self._cap_floor * self._long_short)

        log_rate_ratio = log(forward_rate / self._strike_rate)

        d1 = (log_rate_ratio + (self._reset_date / 2) * volatility ** 2) / (volatility * sqrt(self._reset_date))

        d2 = d1 - volatility * sqrt(self._reset_date)

        return notional_product * (forward_rate * norm.cdf(d1 * float(self._cap_floor)) - self._strike_rate * norm.cdf(
            d2 * float(self._cap_floor)))
