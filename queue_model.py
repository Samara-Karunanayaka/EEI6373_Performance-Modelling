"""
queue_model.py
--------------
Core M/M/c queuing model for the EEI6373 Mini Project
(OPD registration counters case study).

Implements the classic Erlang-C formulas for a multi-server queue with:
  - Poisson arrivals at rate lambda (patients/hour)
  - Exponential service times at rate mu (patients/hour per counter)
  - c identical servers working in parallel, single FCFS queue

Reference: Gross, D., Shortle, J.F., Thompson, J.M. and Harris, C.M. (2018)
Fundamentals of Queueing Theory. 5th edn. Hoboken: Wiley.
"""

import math
import numpy as np
import pandas as pd


def erlang_c(c, lam, mu):
    """
    Compute steady-state performance metrics for an M/M/c queue.

    Parameters
    ----------
    c   : int   -> number of servers (registration counters)
    lam : float -> arrival rate, lambda (patients/hour)
    mu  : float -> service rate per server, mu (patients/hour/counter)

    Returns
    -------
    dict with:
      P0     - probability the system is empty (no patients at all)
      Pwait  - probability an arriving patient must wait (Erlang-C)
      Lq     - expected number of patients waiting in the queue
      Wq     - expected waiting time before being served (hours)
      L      - expected number of patients in the whole system
      W      - expected total time in the system (hours)
      rho    - server utilization = lambda / (c * mu)
      stable - True if rho < 1 (system can keep up with demand)
    """
    a = lam / mu          # offered load, in Erlangs (total "work" arriving per hour)
    rho = a / c            # utilization per server

    # Stability condition: if rho >= 1, demand permanently exceeds
    # total capacity and the queue grows without bound (Wq -> infinity).
    if rho >= 1:
        return dict(P0=np.nan, Pwait=np.nan, Lq=np.inf, Wq=np.inf,
                    L=np.inf, W=np.inf, rho=rho, stable=False)

    # P0: probability of zero patients in the system.
    # Sum of the first c terms of the Poisson-like series, plus a
    # correction term for the "all servers busy" tail (geometric decay).
    sum_terms = sum((a**n) / math.factorial(n) for n in range(c))
    last_term = (a**c) / (math.factorial(c) * (1 - rho))
    P0 = 1 / (sum_terms + last_term)

    # Erlang-C formula: probability an arriving patient finds
    # all c counters busy and must wait.
    Pwait = last_term * P0

    # Little's Law and its derivatives give the rest of the metrics.
    Lq = Pwait * rho / (1 - rho)   # expected queue length
    Wq = Lq / lam                  # expected waiting time (Little's Law: Lq = lambda * Wq)
    W = Wq + 1 / mu                # total time = wait + own service time
    L = lam * W                    # expected number in system (Little's Law: L = lambda * W)

    return dict(P0=P0, Pwait=Pwait, Lq=Lq, Wq=Wq, L=L, W=W, rho=rho, stable=True)


if __name__ == "__main__":
    mu = 20  # service rate per counter (patients/hour), i.e. ~3 min/patient average

    # Three representative daily scenarios (see Table 1 in the report)
    scenarios = {"Off-peak": 15, "Moderate": 30, "Peak": 45}
    c_range = range(1, 7)

    rows = []
    for name, lam in scenarios.items():
        for c in c_range:
            r = erlang_c(c, lam, mu)
            rows.append(dict(Scenario=name, lam=lam, c=c, **r))

    df = pd.DataFrame(rows)
    df.to_csv("mmc_results.csv", index=False)
    print(df.to_string(index=False))
