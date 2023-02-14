# This is a sample Python script.
from product.libor_swaption import LiborSwaption
from yield_curve.libor_curve_builder.libor_bumped_curve_builder import bump_libor_curve
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from yield_curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder
import plotly.express as px

from vol_surface.swaption_vol_surface import AtmSwaptionVolSurface

from product.cash_flow import CashFlow
from product.libor_swap import LiborSwap
from utils.enum import CashFlowFrequency

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    deposits = {1/12: 0.8, 1/6: 1.0, 1/4: 1.3}
    futures = {6/12: 98.4, 9/12: 98.0, 1.0: 97.6, 15/12: 97.3, 18/12: 97.0}
    swap_rate = {2.0: 2.3, 3.0: 2.5, 4.0: 2.7, 5.0: 2.8}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    bumped_curves = bump_libor_curve(curve)

    print(curve.interpolate_discount_factor(3.0))

    cf_product = CashFlow(100000, 1)

    swap_product = LiborSwap(100000, 3, CashFlowFrequency.SEMI_ANNUAL, 0.02)

    par_swap = LiborSwap.par_swap(curve, 1000000, 3, CashFlowFrequency.SEMI_ANNUAL, start_time=1)

    print(swap_product.present_value(curve))

    print(par_swap.present_value(curve))

    print(swap_product.par_rate(curve))

    risk_report = swap_product.first_order_risk(libor_curve=curve)

    for node, risk in risk_report.items():
        print(f"{node}: {risk}")

    print(swap_product.first_order_risk(libor_curve=curve))

    vol = AtmSwaptionVolSurface.from_csv(r"vol_surface/sample_vols.csv")

    swaption = LiborSwaption(par_swap)

    print(swaption.present_value(curve, vol))

    print(curve.interpolate_discount_factor(1))
    #
    # fig = px.scatter(x=yield_curve._t, y=yield_curve._s)
    # fig.show()
