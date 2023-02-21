from enum import IntEnum, Enum


class CashFlowFrequency(IntEnum):
    SEMI_ANNUAL = 2
    ANNUAL = 1
    QUARTERLY = 4
    NONE = 0
    MONTHLY = 12


class CurveInstrument(Enum):
    CASH_DEPOSIT = 1
    IR_FUTURES = 2
    IR_SWAP = 3


class InterpolationType(Enum):
    LINEAR = 1
    CUBIC_SPLINE = 2


class InterestType(Enum):
    SIMPLE = 1
    COMPOUNDING = 2


class PayerReceiver(IntEnum):
    PAYER = 1
    RECEIVER = -1

class OptionType(IntEnum):
    CALL = 1
    PUT = -1

class SwapLegType(Enum):
    FIXED = 0
    FLOATING = 1
