from product.cash_flow import CashFlow
from product.libor_swap import LiborSwap
from utils.enum import CashFlowFrequency, PayerReceiver, OptionType
from vol_surface.swaption_vol_surface import AtmSwaptionVolSurface
from yield_curve.libor_curve import LiborCurve
from math import log, sqrt
from scipy.stats import norm
class LiborSwaption:

    def __init__(self, forward_swap: LiborSwap, option_type: OptionType = OptionType.CALL):

        self._underlying_swap = forward_swap

        self._swaption_expiry = self._underlying_swap.start_time

        self._strike = self._underlying_swap.swap_rate

        self._swap_tenor_years = self._underlying_swap.maturity

        self._notional = self._underlying_swap.notional


    def present_value(self, libor_curve: LiborCurve, swaption_vol_surface: AtmSwaptionVolSurface):

        s_0 = self._underlying_swap.par_rate(libor_curve)

        s_k = self._strike

        vol = swaption_vol_surface.interpolate_vol(self._swaption_expiry, self._swap_tenor_years)

        d_1 = (log(s_0/ self._strike) + 0.5 * self._swaption_expiry * vol**2) / (vol * sqrt(self._swaption_expiry))

        d_2 = d_1 - vol * sqrt(self._swaption_expiry)

        m = int(self._underlying_swap.cash_flow_frequency)

        a = (1/m) * sum([CashFlow(1, t).present_value(libor_curve) for t in self._underlying_swap.times_of_cash_flows])

        l = self._notional

        return l * a * (s_k * norm.cdf(-d_2) - s_0 * norm.cdf(-d_1))

