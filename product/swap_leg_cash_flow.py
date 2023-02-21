from dataclasses import dataclass

from utils.enum import SwapLegType, CashFlowFrequency


@dataclass
class SwapLegCashFlow:
    time: float
    projected_rate: float
    leg_type: SwapLegType
    notional: float
    discount_factor: float
    cash_flow_frequency: CashFlowFrequency

    def get_cash_flow_present_value(self):
        return self.projected_rate * self.notional * self.discount_factor / float(self.cash_flow_frequency)

    def get_cash_flow_future_value(self):
        return self.projected_rate * self.notional / float(self.cash_flow_frequency)

    def as_dict(self):
        d = self.__dict__

        d.update({
            "present_value": self.get_cash_flow_present_value(), "future_value": self.get_cash_flow_future_value()
        })
        return d
