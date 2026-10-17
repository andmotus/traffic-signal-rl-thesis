"""
Section 4.3 and H2: classification-aware state (B) against standard state (A).

Reproduces
    Table 4.3   21 runs per condition: medians, Mann-Whitney U, Holm, rank-biserial r,
                Hodges-Lehmann shift B - A with a 95% percentile bootstrap interval
    Section 4.3 six-run comparison (first round, RESCO/results/multiseed)
    Section 4.3 minimum detectable effect of the design (power simulation)
    Figure 4.3  converged reward and delay of the two state representations

Power simulation (Section 4.3): the standard-state sample of a network is
resampled twice with replacement (21 runs each), a constant shift is added to
one resample, and a two-sided Mann-Whitney test is applied at alpha = 0.025,
the Holm threshold for the more significant of two networks. The minimum
detectable effect is the smallest shift at which at least 80% of 1,500 such
comparisons are significant. The same 1,500 resample pairs are reused for every
candidate shift, so power increases monotonically with the shift and the
threshold is found by bisection.
"""
import numpy as np

from common import (BLUE, BOOTSTRAP_RESAMPLES, FIGURES, NETWORKS, ORANGE, SEED, UNITS, bootstrap_hl_ci,
                    box_with_points, converged_values, fmt, hodges_lehmann, holm, mann_whitney,
                    markdown_table, plot_style, print_utf8, save_csv, training_runs)
from scipy.stats import mannwhitneyu

POWER_SIMULATIONS = 1500
POWER_TARGET = 0.80
POWER_ALPHA = 0.025


def table_4_3(runs):
    rows, csv = [], []
    for metric in ["reward", "delay", "waiting"]:
        res = {}
        for net in NETWORKS:
            a = converged_values(runs[(net, "A")], metric)
            b = converged_values(runs[(net, "B")], metric)
            rng = np.random.default_rng(SEED)
            res[net] = (a, b, mann_whitney(b, a), hodges_lehmann(b, a), bootstrap_hl_ci(b, a, rng))
        p_holm = holm([res[n][2]["p"] for n in NETWORKS])
        for (net, (a, b, test, hl, ci)), ph in zip(res.items(), p_holm):
            d_med = 1 if net == "cologne1" else 2
            d = 1 if (metric == "reward" and net == "cologne1") else 2
            rows.append((net, metric, [f"{NETWORKS[net]}: {metric}{UNITS[metric]}", fmt(np.median(a), d_med),
                                       fmt(np.median(b), d_med), f"{test['U']:.0f}", _p(test["p"]), _p(ph),
                                       fmt(test["r"], 2, sign=True),
                                       f"{fmt(hl, d, sign=True)} [{fmt(ci[0], d, sign=True)}, {fmt(ci[1], d, sign=True)}]"]))
            csv.append([net, metric, len(a), len(b), np.median(a), np.median(b), test["U"], test["p"], ph,
                        test["r"], hl, ci[0], ci[1]])
    rows.sort(key=lambda r: (list(NETWORKS).index(r[0]), ["reward", "delay", "waiting"].index(r[1])))
    save_csv("table_4_3_h2", ["network", "metric", "n_A", "n_B", "median_A", "median_B", "U", "p_raw",
                              "p_holm", "r", "hl_shift_B_minus_A", "ci_low", "ci_high"], csv)
    header = ["Network / metric", "A, median", "B, median", "U", "p (raw)", "Holm p", "r", "Shift B − A [95% CI]"]
    return markdown_table(header, [r[2] for r in rows])


def _p(p):
    return f"{p:.4f}" if p < 0.1 else f"{p:.3f}"


def six_run_test():
    runs6 = training_runs("multiseed")
    lines = []
    for net, label in NETWORKS.items():
        a = converged_values(runs6[(net, "A")], "reward")
        b = converged_values(runs6[(net, "B")], "reward")
        test = mann_whitney(b, a)
        lines.append(f"- {label}, converged reward, {len(a)} vs. {len(b)} runs: U = {test['U']:.0f}, "
                     f"p = {test['p']:.3f}")
    return "\n".join(lines)


def minimum_detectable_effect(sample, rng):
    n = len(sample)
    g1 = sample[rng.integers(0, n, (POWER_SIMULATIONS, n))]
    g2 = sample[rng.integers(0, n, (POWER_SIMULATIONS, n))]

    def power(shift):
        p = mannwhitneyu(g1, g2 + shift, axis=1, alternative="two-sided").pvalue
        return float(np.mean(p < POWER_ALPHA))

    lo, hi = 0.0, float(sample.max() - sample.min())
    while power(hi) < POWER_TARGET:
        hi *= 2
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if power(mid) >= POWER_TARGET else (mid, hi)
    return hi


def power_simulation(runs):
    lines, csv = [], []
    for net, label in NETWORKS.items():
        for metric in ["delay", "reward"]:
            a = converged_values(runs[(net, "A")], metric)
            mde = minimum_detectable_effect(a, np.random.default_rng(SEED))
            rel = mde / abs(np.median(a))
            csv.append([net, metric, mde, np.median(a), rel])
            unit = " reward units" if metric == "reward" else " s"
            lines.append(f"- {label}, {metric}: minimum detectable shift {fmt(mde, 2)}{unit}"
                         f" = {fmt(rel, 1, pct=True)} of the standard-state median ({fmt(np.median(a), 2)})")
    save_csv("power_simulation", ["network", "metric", "minimum_detectable_shift", "median_A", "relative"], csv)
    return "\n".join(lines)


def figure_4_3(runs, plt):
    rng = np.random.default_rng(SEED)
    fig, axs = plt.subplots(2, 2, figsize=(6.3, 5.4),
                            gridspec_kw=dict(hspace=0.12, wspace=0.32, left=0.12, right=0.98, top=0.94, bottom=0.08))
    for j, (net, label) in enumerate(NETWORKS.items()):
        a_r, b_r = (-converged_values(runs[(net, arm)], "reward") for arm in "AB")
        a_d, b_d = (converged_values(runs[(net, arm)], "delay") for arm in "AB")
        ax = axs[0, j]
        box_with_points(ax, 0, a_r, BLUE, rng)
        box_with_points(ax, 1, b_r, ORANGE, rng)
        ax.set_title(label, fontweight="bold")
        if net == "cologne1":
            ax.set_yscale("log")
            ax.set_ylabel("Negative converged reward\n(lower is better, log scale)")
        else:
            ax.set_ylabel("Negative converged reward\n(lower is better)")
        ax.set_xticks([0, 1]); ax.set_xticklabels([]); ax.set_xlim(-0.6, 1.6)
        ax = axs[1, j]
        if net == "cologne1":
            lim = (25, 53)
            for x, d, c in [(0, a_d, BLUE), (1, b_d, ORANGE)]:
                box_with_points(ax, x, d, c, rng)
                out = np.sort(d[d > lim[1]])
                if len(out):
                    lab = (f"{len(out)} runs outside\n(" + ", ".join(f"{v:.0f} s" for v in out) + ")"
                           if len(out) > 1 else f"1 run outside\n({out[0]:.0f} s)")
                    ax.scatter([x], [lim[1] - 0.4], marker="^", color=c, s=22, zorder=4, clip_on=False)
                    ax.text(x, lim[1] - 1.0, lab, va="top", ha="center", fontsize=7.5, color="#555")
            ax.set_ylim(*lim)
        else:
            box_with_points(ax, 0, a_d, BLUE, rng)
            box_with_points(ax, 1, b_d, ORANGE, rng)
        ax.set_ylabel("Converged delay (s)")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Standard (A)", "Classification-\naware (B)"])
        ax.set_xlim(-0.6, 1.6)
    fig.savefig(FIGURES / "Figure_4_3_h2_reward_delay.png")
    plt.close(fig)


def main():
    plt = plot_style()
    runs = training_runs("multiseed21")
    figure_4_3(runs, plt)
    return "\n\n".join([
        "## Section 4.3: H2",
        "### Table 4.3",
        table_4_3(runs),
        f"Bootstrap: {BOOTSTRAP_RESAMPLES:,} resamples, numpy default_rng({SEED}) restarted for every row.",
        "### Six-run comparison (first round)",
        six_run_test(),
        "### Minimum detectable effect (power simulation)",
        power_simulation(runs),
        "Figure: `Figure_4_3_h2_reward_delay.png`.",
    ])


if __name__ == "__main__":
    print_utf8(main())
