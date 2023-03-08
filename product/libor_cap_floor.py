from math import log, sqrt

from scipy.stats import norm

from yield_curve.libor_curve import LiborCurve


class Caplet:

    def __init__(self, notional: float, strike_rate: float, reset_date: float, payoff_date: float):
        self._notional = notional

        self._strike_rate = strike_rate

        self._reset_date = reset_date

        self._payoff_date = payoff_date

        self._period = payoff_date - reset_date

    def present_value(self, libor_curve: LiborCurve, volatility: float):

        forward_rate = libor_curve.interpolate_forward_rate(self._reset_date, self._period)

        notional_product = forward_rate * self._period * libor_curve.interpolate_discount_factor(self._payoff_date)

        log_rate_ratio = log(forward_rate / self._strike_rate)

        d1 = (log_rate_ratio + (self._reset_date / 2) * volatility ** 2) / (volatility * sqrt(self._reset_date))

        d2 = d1 - volatility * sqrt(self._reset_date)

        return notional_product * (forward_rate * norm.cdf(d1) - self._reset_date * norm.cdf(d2))
