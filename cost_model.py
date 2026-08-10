

import pandas as pd
from queue_model import erlang_c

mu = 20  # service rate per counter (patients/hour) - must match queue_model.py

if __name__ == "__main__":
    # Cost trade-off analysis for the Peak scenario (lambda = 45/hr)
    lam_peak = 45
    Cs = 800   # cost of operating one counter per hour (staff wage + overhead, LKR)
    Cw = 150   # imputed cost of one patient-hour of waiting (LKR)

    rows = []
    for c in range(3, 8):
        r = erlang_c(c, lam_peak, mu)
        server_cost = c * Cs
        wait_cost = lam_peak * r["Wq"] * Cw
        total_cost = server_cost + wait_cost
        rows.append(dict(c=c, Wq_min=r["Wq"] * 60, rho=r["rho"], Pwait=r["Pwait"],
                          server_cost=server_cost, wait_cost=wait_cost, total_cost=total_cost))

    cost_df = pd.DataFrame(rows)
    cost_df.to_csv("cost_results.csv", index=False)
    print(cost_df.to_string(index=False))
