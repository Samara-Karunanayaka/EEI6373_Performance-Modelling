import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
})

df = pd.read_csv("mmc_results.csv")
cost = pd.read_csv("cost_results.csv")
colors = {"Off-peak": "#2a9d8f", "Moderate": "#e9c46a", "Peak": "#e76f51"}

# ---- Chart 1: Waiting time vs number of counters ----
fig, ax = plt.subplots(figsize=(7, 4.5))
for name, g in df.groupby("Scenario"):
    g = g[g["stable"] == True].sort_values("c")
    ax.plot(g["c"], g["Wq"]*60, marker="o", label=name, color=colors[name], linewidth=2)
ax.axhline(5, color="grey", linestyle="--", linewidth=1, label="5-min service target")
ax.set_xlabel("Number of registration counters (c)")
ax.set_ylabel("Average waiting time, Wq (minutes)")
ax.set_title("Average Waiting Time vs. Number of Counters")
ax.legend()
fig.tight_layout()
fig.savefig("chart_wq_vs_c.png", dpi=170)
plt.close(fig)

# ---- Chart 2: Utilization vs number of counters ----
fig, ax = plt.subplots(figsize=(7, 4.5))
for name, g in df.groupby("Scenario"):
    g = g[g["stable"] == True].sort_values("c")
    ax.plot(g["c"], g["rho"]*100, marker="s", label=name, color=colors[name], linewidth=2)
ax.axhline(80, color="grey", linestyle="--", linewidth=1, label="80% utilization threshold")
ax.set_xlabel("Number of registration counters (c)")
ax.set_ylabel("Server utilization, ρ (%)")
ax.set_title("Counter Utilization vs. Number of Counters")
ax.legend()
fig.tight_layout()
fig.savefig("chart_rho_vs_c.png", dpi=170)
plt.close(fig)

# ---- Chart 3: Probability of waiting (Erlang C) vs c ----
fig, ax = plt.subplots(figsize=(7, 4.5))
for name, g in df.groupby("Scenario"):
    g = g[g["stable"] == True].sort_values("c")
    ax.plot(g["c"], g["Pwait"]*100, marker="^", label=name, color=colors[name], linewidth=2)
ax.set_xlabel("Number of registration counters (c)")
ax.set_ylabel("P(wait > 0)  (%)")
ax.set_title("Probability an Arriving Patient Must Wait (Erlang C)")
ax.legend()
fig.tight_layout()
fig.savefig("chart_pwait_vs_c.png", dpi=170)
plt.close(fig)

# ---- Chart 4: Cost trade-off at peak load ----
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(cost["c"], cost["server_cost"], marker="o", label="Staffing cost", color="#264653")
ax.plot(cost["c"], cost["wait_cost"], marker="o", label="Patient waiting cost", color="#e76f51")
ax.plot(cost["c"], cost["total_cost"], marker="o", label="Total cost", color="#e9c46a", linewidth=3)
best_c = cost.loc[cost["total_cost"].idxmin(), "c"]
ax.axvline(best_c, color="grey", linestyle="--", linewidth=1)
ax.set_xlabel("Number of registration counters (c)")
ax.set_ylabel("Cost per hour (LKR)")
ax.set_title("Cost Trade-off Analysis — Peak Load (λ = 45/hr)")
ax.legend()
fig.tight_layout()
fig.savefig("chart_cost_tradeoff.png", dpi=170)
plt.close(fig)

# ---- Diagram: M/M/c schematic ----
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")

# Arrivals
ax.annotate("", xy=(2.1, 3), xytext=(0.2, 3),
            arrowprops=dict(arrowstyle="->", lw=2, color="#264653"))
ax.text(1.1, 3.35, "Arrivals\nλ (Poisson)", ha="center", fontsize=10)

# Queue box
queue_box = mpatches.FancyBboxPatch((2.2, 2.3), 2.0, 1.4, boxstyle="round,pad=0.05",
                                     linewidth=1.5, edgecolor="#264653", facecolor="#f4f1de")
ax.add_patch(queue_box)
ax.text(3.2, 3.0, "Waiting line\n(FCFS)", ha="center", va="center", fontsize=10)

# Arrow to servers
ax.annotate("", xy=(4.6, 3), xytext=(4.2, 3),
            arrowprops=dict(arrowstyle="->", lw=2, color="#264653"))

# Servers (c counters)
server_labels = ["Counter 1\nμ", "Counter 2\nμ", "Counter c\nμ"]
ys = [4.6, 3.0, 1.0]
for i, (lab, y) in enumerate(zip(server_labels, ys)):
    box = mpatches.FancyBboxPatch((4.7, y-0.5), 1.7, 1.0, boxstyle="round,pad=0.05",
                                   linewidth=1.5, edgecolor="#2a9d8f", facecolor="#e9f5f3")
    ax.add_patch(box)
    ax.text(5.55, y, lab, ha="center", va="center", fontsize=9)
    ax.annotate("", xy=(4.7, y), xytext=(4.2, 3),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#2a9d8f", alpha=0.7))
    ax.annotate("", xy=(8.2, y), xytext=(6.4, y),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#e76f51", alpha=0.8))
ax.text(6.9, 5.4, "⋮", fontsize=16, ha="center")

ax.text(9.0, 3.0, "Departures\n(registered\npatients)", ha="center", fontsize=10)

ax.text(5.55, 5.9, "M/M/c Queuing Model — OPD Registration", ha="center", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig("diagram_mmc.png", dpi=170)
plt.close(fig)

print("charts done")
