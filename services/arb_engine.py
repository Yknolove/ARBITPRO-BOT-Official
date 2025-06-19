from typing import Dict, List, Tuple

class ArbEngine:
    def __init__(self, thresholds: Dict[Tuple[str,str], dict]):
        self.thresholds = thresholds

    def find_arbitrage(self, rates: Dict[str, dict]) -> List[Tuple[str,str,float]]:
        res = []
        keys = list(rates)
        for i in range(len(keys)):
            for j in range(len(keys)):
                if i == j:
                    continue
                A, B = keys[i], keys[j]
                ask = rates[A]["sell"]
                bid = rates[B]["buy"]
                profit = (bid - ask)/ask*100
                cfg = self.thresholds.get((A,B), {})
                if profit >= cfg.get("min_profit", 0):
                    res.append((A,B,round(profit,2)))
        return res
