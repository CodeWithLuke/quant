from datetime import date
from typing import List

import numpy as np

from instrument_yield_curve.curve_instruments.abs_curve_instrument import AbsCurveInstrument
from instrument_yield_curve.curve_point import CurvePoint


class InstrumentYieldCurveConstructor:

    def __init__(self, base_date: date, market_quotes: list[AbsCurveInstrument]):
        get_quote_date = lambda m: m.node_date
        market_quotes.sort(key=get_quote_date)

        n_nodes = len(market_quotes)

        self._base_date = base_date
        self._market_quotes = market_quotes

        self._zero_rate_points: List[CurvePoint] = []
        self._zero_rate_times = np.zeros(n_nodes)
        self._zero_rate_rates = np.zeros(n_nodes)


    def build_yield_curve(self):
    