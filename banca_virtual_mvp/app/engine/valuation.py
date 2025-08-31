from dataclasses import dataclass
from typing import Dict, Any, Tuple
import math

@dataclass
class ScorecardInputs:
    team: float
    product: float
    market: float
    traction: float
    moat: float

def scorecard_valuation(x: ScorecardInputs, base: float = 5_000_000.0) -> float:
    # weights can be adjusted; simple average applied to a base max valuation
    w = {"team":0.25,"product":0.20,"market":0.25,"traction":0.20,"moat":0.10}
    s = (
        x.team*w["team"]
        + x.product*w["product"]
        + x.market*w["market"]
        + x.traction*w["traction"]
        + x.moat*w["moat"]
    )  # 0–1
    return base * s

def vc_method(post_money_target: float, ownership: float, discount: float, years: int) -> float:
    # Reverse discounted valuation for a target exit and target ownership
    # ownership as decimal (e.g., 0.2 for 20%); discount as decimal (0.5 for 50% annual)
    pv_exit = post_money_target * ownership
    return pv_exit / ((1 + discount) ** years)

def dcf_simple(revenue_year1: float, growth: float, margin: float, years: int, discount: float, terminal_growth: float = 0.02) -> float:
    # very simplified FCFF as revenue * margin; no WC/capex detail; for MVP only
    cashflows = []
    rev = revenue_year1
    for t in range(1, years+1):
        fcff = rev * margin
        cashflows.append(fcff / ((1 + discount) ** t))
        rev *= (1 + growth)
    # terminal
    fcff_terminal = rev * margin
    terminal_value = (fcff_terminal * (1 + terminal_growth)) / (discount - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount) ** years)
    return sum(cashflows) + pv_terminal
