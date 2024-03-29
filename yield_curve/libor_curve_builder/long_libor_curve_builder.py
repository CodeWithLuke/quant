from typing import Dict, List

import numpy as np

from utils.constants import FLOAT_EQ_THRESHOLD
from utils.utils import spot_rate_to_discount, discount_to_spot_rate


class LongLiborCurveBuilder:
    _key_f = lambda dp: dp['time']

    _val_f = lambda dp: dp['value']

    def __init__(self, previous_libor_data_points: List[Dict[str, float]], swap_quotes: Dict[float, float]):

        self._swap_quotes = swap_quotes

        self._t = np.array(list(swap_quotes.keys()))

        self._s = np.array(list(swap_quotes.values()))

        previous_points_t = []
        previous_points_s = []
        for point in previous_libor_data_points:
            previous_points_t.append(point['time'])
            previous_points_s.append(point['spot_rate'])

        previous_points_t = np.array(previous_points_t)
        previous_points_s = np.array(previous_points_s)

        self._discount_factors_sum = 0

        self._iter_t = 0.5

        discount_factor = spot_rate_to_discount(
            np.interp(self._iter_t, previous_points_t, previous_points_s, right=np.nan, left=0), self._iter_t)

        while not np.isnan(discount_factor):
            self._discount_factors_sum += discount_factor
            self._iter_t += 0.5
            discount_factor = spot_rate_to_discount(
                np.interp(self._iter_t, previous_points_t, previous_points_s, right=np.nan, left=1), self._iter_t)

        self.curve = self.build_curve()

    def interpolate_swap_rates(self, t_interp):
        y_interp = np.interp(t_interp, self._t, self._s)
        return y_interp

    # scale swap rate

    def get_discount_factor_from_swap_rate(self, swap_quote):

        swap_quote /= 100

        discount_factor = (2 - swap_quote * self._discount_factors_sum) / (2 + swap_quote)

        return discount_factor

    def build_curve(self):
        long_curve = []

        for t, s in self._swap_quotes.items():

            while abs(t - self._iter_t) > FLOAT_EQ_THRESHOLD:
                self._discount_factors_sum += self.get_discount_factor_from_swap_rate(
                    self.interpolate_swap_rates(self._iter_t)
                )

                self._iter_t += 0.5

            spot_rate = discount_to_spot_rate(
                self.get_discount_factor_from_swap_rate(self.interpolate_swap_rates(t)), t
            )

            long_curve.append({'time': t, 'spot_rate': spot_rate})

        return long_curve
