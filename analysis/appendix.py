"""
Appendices A and B, and Figure 3.2.

Reproduces
    Table A.1   converged reward of Fixed-Time and Max-Pressure on Cologne1, typed and original demand
    Appendix B  the two development comparisons at 100 and 200 episodes
    Table B.1   severe episodes after the end of exploration, all 84 multi-seed runs
    Figure 3.2  two Cologne1 training runs illustrating the instability

Table A.1 and the development comparisons use the mean of the final 20 logged
episodes, the summary used during development (Appendix B explains why the
thesis later switched to the median).
"""
import numpy as np

from common import (BLUE, EPSILON_END, FIGURES, NETWORKS, ORANGE, converged, fmt, markdown_table,
                    plot_style, print_utf8, save_csv, series, single_run, training_runs)

# Table A.1: single development runs (RESCO/results/)
TABLE_A1 = {"Typed (KBA-calibrated)": ("dd755fd4be898a0f", "d40ac3cf13edbf84"),
            "Original (cars only)": ("a6f1b0e99efba1b0", "ef990d6ac56ce5b6")}

# Appendix B: development comparisons of the two states, one run each
DEV_100 = {"cologne1": ("d54ffcc727ee4d07", "6be2c83b144a1b84")}                  # (A, B), 100 episodes
DEV_200 = {"cologne1": ("d54ffcc773f38aed", "6be2c83b9597054a"),                  # (A, B), 200 episodes
           "ingolstadt1": ("709812e3b446719f", "d58a07c3d04c77d0")}

# Figure 3.2: two Cologne1 runs from the multi-seed set
FIG_3_2 = {"A": "d54ffcc773f38aed", "B": "6be2c83b5b164cee"}

# Severe episode (Appendix B): below -5,000 on Cologne1; more than 20 times the run's own converged
# median on Ingolstadt1
COLOGNE_SEVERE = -5000
INGOLSTADT_SEVERE_FACTOR = 20
SPIKE_FACTOR = 20          # isolated spike in the development runs, relative to the neighbouring episodes


def table_a1():
    rows, csv_rows = [], []
    for demand, (ft_hash, mp_hash) in TABLE_A1.items():
        ft = series(single_run(ft_hash), "reward")[-20:].mean()
        mp = series(single_run(mp_hash), "reward")[-20:].mean()
        rows.append([demand, fmt(ft, 2), fmt(mp, 2), f"{mp / ft:.0f}×"])
        csv_rows.append([demand, ft, mp, mp / ft])
    save_csv("table_a_1_maxpressure", ["demand", "fixed_time", "max_pressure", "ratio"], csv_rows)
    return markdown_table(["Demand", "Fixed-Time", "Max-Pressure", "Ratio"], rows)


def spikes(values, factor=SPIKE_FACTOR, window=5):
    """Episodes (1-based) whose reward is more than `factor` times worse than the median of the
    `window` episodes before and after it."""
    out = []
    for i, v in enumerate(values):
        neighbours = np.r_[values[max(0, i - window):i], values[i + 1:i + 1 + window]]
        if v < factor * np.median(neighbours):
            out.append(i + 1)
    return out


def development_runs():
    lines = []
    for label, runs in [("100 episodes", DEV_100), ("200 episodes", DEV_200)]:
        for net, (a, b) in runs.items():
            ra, rb = series(single_run(a), "reward"), series(single_run(b), "reward")
            lines.append(f"- {NETWORKS[net]}, {label}: mean of the final 20 logged episodes A {fmt(ra[-20:].mean(), 2)}, "
                         f"B {fmt(rb[-20:].mean(), 2)}; worst episode A {fmt(ra.min(), 0)} (episode {ra.argmin() + 1}), "
                         f"B {fmt(rb.min(), 0)} (episode {rb.argmin() + 1}); isolated spikes A {spikes(ra)}, B {spikes(rb)}")
    lines.append(f"  (isolated spike: reward more than {SPIKE_FACTOR} times worse than the median of the five "
                 "episodes before and after it)")
    return "\n".join(lines)


def severe(values, net):
    if net == "cologne1":
        return values < COLOGNE_SEVERE
    return values < INGOLSTADT_SEVERE_FACTOR * converged(values)


def longest_streak(flags):
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def table_b1(runs):
    rows, csv_rows = [], []
    for net, label in NETWORKS.items():
        for arm, name in [("A", "Standard (A)"), ("B", "Classification-aware (B)")]:
            streaks, any_severe = [], 0
            for p in runs[(net, arm)]:
                r = series(p, "reward")
                flags = severe(r, net)[EPSILON_END:]      # episodes 161 onwards
                any_severe += bool(flags.any())
                streaks.append(longest_streak(flags))
            five = sum(s >= 5 for s in streaks)
            rows.append([label, name, any_severe, five, max(streaks)])
            csv_rows.append([net, arm, any_severe, five, max(streaks)])
    save_csv("table_b_1_severe_episodes", ["network", "arm", "runs_with_severe", "runs_with_5_consecutive",
                                           "longest_streak"], csv_rows)
    return markdown_table(["Network", "State", "Runs with ≥ 1 severe episode", "Runs with ≥ 5 consecutive",
                           "Longest streak"], rows)


def figure_3_2(plt):
    ra, rb = (-series(single_run(FIG_3_2[k], "multiseed21"), "reward") for k in "AB")
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.3)
    ep = np.arange(1, len(ra) + 1)
    ax.axvspan(len(ra) - 19, len(ra) + 1, color="#e8e8e8", lw=0)
    ax.text(len(ra) - 9, 2.5e5, "final 20\nepisodes", ha="center", va="center", fontsize=7.5, color="#555")
    ax.plot(ep, ra, color=BLUE, lw=1.0, label="Standard state, seed A: isolated post-decay spike "
                                                   f"(episode {int(np.argmax(ra[EPSILON_END:]) + EPSILON_END + 1)})")
    ax.plot(ep, rb, color=ORANGE, lw=1.0, label="Classification-aware state, seed B: sustained collapse")
    ax.axvline(EPSILON_END, color="#555", ls="--", lw=0.9)
    ax.text(EPSILON_END - 2, 2.6e5, f"ε reaches 0 (ep. {EPSILON_END})", ha="right", va="center", fontsize=7.5, color="#555")
    ax.set_yscale("log")
    ax.set_ylim(100, 4.5e5)
    ax.set_xlim(0, 200)
    ax.set_xlabel("Training episode")
    ax.set_ylabel("Negative episode reward\n(log scale, lower is better)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False, fontsize=7.5)
    fig.savefig(FIGURES / "Figure_3_2_instability.png")
    plt.close(fig)
    return (f"- Converged reward (median of the final 20 logged episodes): seed A {fmt(converged(-ra), 0)}, "
            f"seed B {fmt(converged(-rb), 0)}; the figure plots the negative reward")


def main():
    plt = plot_style()
    runs = training_runs("multiseed21")
    return "\n\n".join([
        "## Appendix A",
        "### Table A.1",
        table_a1(),
        "Mean reward over the final 20 logged episodes of single development runs.",
        "## Appendix B",
        "### Development comparisons",
        development_runs(),
        "### Table B.1",
        table_b1(runs),
        "### Figure 3.2",
        figure_3_2(plt),
        "Figure: `Figure_3_2_instability.png`.",
    ])


if __name__ == "__main__":
    print_utf8(main())
