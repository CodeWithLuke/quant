# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from curve.libor_curve_builder.libor_curve_builder import LiborCurveBuilder
import plotly.express as px

from product.cash_flow import CashFlow

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    deposits = {1/12: 0.8, 1/6: 1.0, 1/4: 1.3}
    futures = {6/12: 98.4, 9/12: 98.0, 1.0: 97.6, 15/12: 97.3, 18/12: 97.0}
    swap_rate = {2.0: 2.3, 4.0: 2.7}
    fcb = LiborCurveBuilder(deposits, futures, swap_rate)
    curve = fcb.curve()

    cf_product = CashFlow(100000, 1)

    print(cf_product.present_value(curve))

    # print(curve.interpolate_discount_factor(1))
    #
    # fig = px.scatter(x=curve._t, y=curve._s)
    # fig.show()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
