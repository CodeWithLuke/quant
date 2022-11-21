from utils.conversion import discount_to_spot_rate
import numpy as np

class MarketBond:
    def __init__(self, price: float, face_value: float, maturity: int,
                 coupon_rate=np.nan, coupon_frequency=np.nan, yield_curve=np.nan):
        self._price = price
        self._face_value = face_value
        self._maturity = maturity
        if not np.isnan(coupon_rate):
            assert not np.isnan(coupon_frequency)
            self._coupon_rate = coupon_rate
            self._maturity = maturity

    def _calculate_yield(self):
        if np.isnan(self._coupon_rate):
            discount_factor = self._price/self._face_value
            return discount_to_spot_rate(discount_factor, self._maturity)

        else
