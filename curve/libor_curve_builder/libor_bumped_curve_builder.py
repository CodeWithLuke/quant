from curve.libor_curve import LiborCurve
from curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder
from utils.constants import BASIS_POINT_CONVERSION

from copy import deepcopy


def bump_libor_curve(libor_curve: LiborCurve, n_bps_bump=1):

    bumped_curves = dict()

    market_data = libor_curve.market_quotes

    for curve_instrument, quotes in market_data.items():

        market_data_copy = deepcopy(market_data)

        for time, quote in quotes.items():

            curve_instrument_quotes_copy = deepcopy(market_data[curve_instrument])

            curve_instrument_quotes_copy[time] += n_bps_bump * BASIS_POINT_CONVERSION

            market_data_copy[curve_instrument] = curve_instrument_quotes_copy

            time_str = f"{round(time)}Y" if time.is_integer() else f"{round(time*12)}M"

            bumped_curves["_".join((curve_instrument.name, time_str))] = LiborCurveBuilder.from_market_data_dict(
                market_data_copy).curve()

    return bumped_curves
