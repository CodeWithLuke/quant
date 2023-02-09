from typing import Dict
from utils.utils import spot_rate_to_discount, discount_to_spot_rate, future_price_to_forward_rate

class MidLiborCurveBuilder:

    def __init__(self, futures_prices: Dict[float, float], short_curve):
        self._future_prices = futures_prices
        self.curve = short_curve
        self.curve += self.build_curve()

    @staticmethod
    def extend_libor_rate_with_forward_rate(libor_data_point, t, forward_rate):
        first_point_time = libor_data_point['time']
        first_point_discount = spot_rate_to_discount(
            libor_data_point['spot_rate'], first_point_time)
        delta_t = t - first_point_time
        discount_factor = first_point_discount / (1 + delta_t * forward_rate)
        return discount_to_spot_rate(discount_factor, t)


    def build_curve(self):
        mid_curve = []

        for t, fp in self._future_prices.items():
            if mid_curve:
                last_data_point = max(mid_curve, key=lambda dp: dp['time'])
            else:
                last_data_point = max(self.curve, key=lambda dp: dp['time'])
            forward_rate = future_price_to_forward_rate(fp)
            data_point = {'time': t, 'spot_rate': self.extend_libor_rate_with_forward_rate(
                last_data_point, t, forward_rate)}
            mid_curve.append(data_point)
        mid_curve.sort(key=lambda dp: dp['time'])

        return mid_curve
