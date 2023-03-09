from math import log, sqrt

from scipy.stats import norm

from utils.enum import CapFloor, LongShort
from yield_curve.libor_curve import LiborCurve


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

        return notional_product * (forward_rate * norm.cdf(d1 * float(self._cap_floor)) - self._reset_date * norm.cdf(
            d2 * float(self._cap_floor)))
