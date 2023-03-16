from math import exp

from scipy.optimize import newton

from utils.enum import CashFlowFrequency
from yield_curve.libor_curve import LiborCurve


class FixedRateBond:
    def __init__(self, notional: float, maturity: float, coupon_frequency: CashFlowFrequency,
                 coupon_rate: float = None):
        self.notional = notional
        self.maturity = maturity
        self._has_coupons = coupon_frequency is not None and not coupon_frequency == CashFlowFrequency.NONE
        if self._has_coupons:
            assert coupon_rate is not None
        self.coupon_frequency = coupon_frequency
        self.coupon_period = 1 / int(coupon_frequency)
        self.coupon_rate = coupon_rate
        self.num_coupon_payments = int(int(coupon_frequency) * maturity)

    def present_value(self, libor_curve, applied_z_spread=0):
        coupon_amount = self.notional * self.coupon_rate * self.coupon_period

        value = self.notional * exp(-1 * self.maturity * (libor_curve.interpolate_curve(self.maturity) + applied_z_spread))

        for i in range(1, self.num_coupon_payments + 1):
            t = i * self.coupon_period

            ir_yield = libor_curve.interpolate_curve(t)

            value += coupon_amount * self.coupon_period * exp(-1 * t * (ir_yield + applied_z_spread))

        return value

    def yield_to_price(self, yield_rate: float):
        coupon_amount = self.notional * self.coupon_rate * self.coupon_period

        coupon_present_value_sum = sum(
            [coupon_amount * exp(-i * self.coupon_period * yield_rate) for i in range(1, self.num_coupon_payments + 1)]
        )

        return coupon_present_value_sum + self.notional * exp(-1 * self.maturity * yield_rate)

    def price_to_yield(self, price: float):
        def _f(y): return self.yield_to_price(y) - price

        return newton(_f, 0.0)

    def get_par_yield(self, yield_rate: float):
        annuity = sum(
            [exp(-i * self.coupon_period * yield_rate) for i in range(1, self.num_coupon_payments + 1)]
        )

        return (1 - exp(-1 * self.maturity * yield_rate)) * self.maturity / annuity

    def get_bond_duration_from_yield(self, yield_rate: float):
        coupon_amount = self.notional * self.coupon_rate * self.coupon_period

        coupon_time_weighted_present_value_sum = sum([
            i * self.coupon_period * coupon_amount * exp(-i * self.coupon_period * yield_rate) for i in range(
                1, self.num_coupon_payments + 1
            )
        ])

        return coupon_time_weighted_present_value_sum + self.maturity * self.notional * exp(
            -1 * self.maturity * yield_rate
        )

    def get_z_spread(self, price: float, libor_curve: LiborCurve):

        def _f(z): return self.present_value(libor_curve, z) - price

        return newton(_f, 0)


