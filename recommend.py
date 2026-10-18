"""Recommendation layer: rebalance entrances + suggest nearby time slots."""
import numpy as np, pandas as pd
from config import STATION


def entrance_plan(code, pred_entries, max_shift=0.35, target=0.85):
    """Greedily move passengers from overloaded to under-used entrances.
    max_shift = max share of an entrance's load we assume can be redirected."""
    st = STATION[code]
    ents = st["entrances"]
    orig = np.array([e["share"] for e in ents]) * pred_entries
    caps = np.array([e["cap_share"] for e in ents]) * st["capacity"]
    loads, budget = orig.copy(), max_shift * orig
    for _ in range(100):
        util = loads / caps
        src = int(np.argmax(np.where(budget > 1, util, -1)))
        dst = int(np.argmin(util))
        if budget[src] <= 1 or util[src] <= target or util[dst] >= target:
            break
        amt = min(loads[src] - target*caps[src],
                  target*caps[dst] - loads[dst], budget[src])
        if amt <= 1:
            break
        loads[src] -= amt; loads[dst] += amt; budget[src] -= amt
    return pd.DataFrame(dict(
        entrance=[e["name"] for e in ents],
        before=(orig/caps).round(2), after=(loads/caps).round(2),
        passengers_shifted=(loads - orig).round(0).astype(int)))


def best_shift(cong_by_hour, hour, window=2):
    """Quietest hour within +/- window hours. Returns (hour, now, then)."""
    cands = {h: c for h, c in cong_by_hour.items() if abs(h - hour) <= window}
    best = min(cands, key=cands.get)
    return best, cong_by_hour[hour], cands[best]
