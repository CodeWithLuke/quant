from yield_curve.abs_curve import AbsCurve


class CashFlow:

    def __init__(self, notional, t):
        self._notional = notional

        self._t = t

    def present_value(self, model: AbsCurve):

        return self._notional * model.interpolate_discount_factor(self._t)
