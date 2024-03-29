from math import exp, log


def spot_rate_to_discount(r: float, t: float) -> float:
    return exp(-1 * r * t)


def discount_to_spot_rate(z: float, t: float) -> float:
    return -1 * log(z) / t


def future_price_to_forward_rate(future_price):
    return (100 - future_price) / 100
