from typing import Dict

from utils.utils import discount_to_spot_rate


class ShortLiborCurveBuilder:

    def __init__(self, libor_rates: Dict[float, float]):
        self._libor_rates = libor_rates
        self.curve = self.build_curve()

    @staticmethod
    def libor_rate_to_discount(l, t):
        return 1 / (1 + t * l / 100)

    def build_curve(self):
        curve = []

        for t, lr in self._libor_rates.items():
            discount_rate = self.libor_rate_to_discount(lr, t)
            data_point = {'time': t, 'spot_rate': discount_to_spot_rate(
                discount_rate, t
            )}
            curve.append(data_point)
        curve.sort(key=lambda dp: dp['time'])

        return curve
