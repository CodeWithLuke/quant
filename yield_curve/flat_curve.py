from utils.utils import spot_rate_to_discount
from yield_curve.abs_curve import AbsCurve


class FlatCurve(AbsCurve):

    def __init__(self, spot_rate: float):
        self._spot_rate = spot_rate

    def interpolate_curve(self, t):
        return self._spot_rate

    def interpolate_discount_factor(self, t):
        return spot_rate_to_discount(self._spot_rate, t)