from enum import IntEnum, Enum


class CashFlowFrequency(IntEnum):
    SEMI_ANNUAL = 2
    ANNUAL = 1
    QUARTERLY = 4
    MONTHLY = 12


class CurveInstrument(Enum):
    CASH_DEPOSIT = 1
    IR_FUTURES = 2
    IR_SWAP = 3


class InterpolationType(Enum):
    LINEAR = 1
    CUBIC_SPLINE = 2


class CompoundingType(Enum):
    SIMPLE = 1
    CONTINUOUS = 2


# For swap this is relative to the fixed rate
class PayerReceiver(IntEnum):
    PAYER = 1
    RECEIVER = -1


class LongShort(IntEnum):
    LONG = 1
    SHORT = -1


class OptionType(IntEnum):
    CALL = 1
    PUT = -1


class SwapLegType(Enum):
    FIXED = 0
    FLOATING = 1


class CapFloor(IntEnum):
    CAP = 1
    FLOOR = -1


class DayCountConventions(Enum):
    DCC_ACTUAL_ACTUAL = 0
    DCC_30_360 = 1
    DCC_ACTUAL_365 = 2