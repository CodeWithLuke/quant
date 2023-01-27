from enum import IntEnum


class CashFlowFrequency(IntEnum):
    SEMI_ANNUAL = 2
    ANNUAL = 1
    QUARTERLY = 4
    NONE = 0
    MONTHLY = 12
