"""
Section 4.1 and H1: plausibility checks and standard-state IDQN against Fixed-Time.

Reproduces
    Table 4.1   IDQN delay compared with the published RESCO benchmark
    Section 4.1 effect of the vehicle-type injection on Fixed-Time (Cologne1)
    Table 4.2   converged performance of standard-state IDQN compared with Fixed-Time
    Section 4.2 spread of the converged delays, learning-curve crossing, Max-Pressure on Ingolstadt1
    Figure 4.1  average delay per vehicle during training
    Figure 4.2  converged delay of standard-state IDQN compared with Fixed-Time

Reference sample for H1 (Section 3.6): the 100 episodes of the Fixed-Time CO2
validation run on the same network, against the 21 converged medians of the
standard-state runs. Holm correction across the two networks, per metric.
"""
import numpy as np
from matplotlib.patches import ConnectionPatch, Rectangle

from common import (BLUE, EPSILON_END, FIGURES, GRAY, NETWORKS, ORANGE, SEED, UNITS, box_with_points,
                    converged_values, emissions_run, fmt, fmt_p, holm, mann_whitney, markdown_table,
                    plot_style, print_utf8, relative_change, save_csv, series, single_run, training_runs)

# Ault & Sharon (2021), Table 1: IDQN average delay (s) on the original, cars-only demand, 5 runs
PUBLISHED_IDQN_DELAY = {"cologne1": 26.05, "ingolstadt1": 21.48}

UNTYPED_FIXED_COLOGNE1 = "a6f1b0e99efba1b0"     # Fixed-Time on the original Cologne1 demand (setup phase)
MAXPRESSURE_INGOLSTADT1 = "9104c6d8f9add157"     # Max-Pressure, typed Ingolstadt1, 100 episodes
IDQN_200_INGOLSTADT1 = "709812e3b446719f"        # standard-state IDQN, typed Ingolstadt1, 200 episodes


def table_4_1(runs):
    rows, csv = [], []
    for net, label in NETWORKS.items():
        delays = [series(p, "delay") for p in runs[(net, "A")]]
        best = np.array([d.min() for d in delays])
        conv = converged_values(runs[(net, "A")], "delay")
        pub = PUBLISHED_IDQN_DELAY[net]
        rows.append([f"{label}, average delay (s)", fmt(pub, 2),
                     f"{fmt(best.mean(), 2)} (median {fmt(np.median(best), 2)})", fmt(np.median(conv), 2),
                     fmt(relative_change(best.mean(), pub), 1, sign=True, pct=True)])
        csv.append([net, pub, best.mean(), np.median(best), np.median(conv), relative_change(best.mean(), pub)])
    save_csv("table_4_1_benchmark", ["network", "published", "best_episode_mean", "best_episode_median",
                                     "converged_median", "best_vs_published"], csv)
    header = ["", "Published (Ault & Sharon, 2021)", "This thesis, best episode",
              "This thesis, converged median", "Best episode vs. published"]
    return markdown_table(header, rows)


def injection_check():
    typed, untyped = emissions_run("cologne1", "fixed"), single_run(UNTYPED_FIXED_COLOGNE1)
    lines = []
    for metric in ["delay", "waiting"]:
        t, u = series(typed, metric), series(untyped, metric)
        test = mann_whitney(t, u)
        lines.append(f"- Fixed-Time {metric}{UNITS[metric]}, original -> typed demand: "
                     f"{fmt(np.median(u), 1)} -> {fmt(np.median(t), 1)} "
                     f"({fmt(relative_change(np.median(t), np.median(u)), 1, sign=True, pct=True)}), "
                     f"Mann-Whitney p = {test['p']:.1e} (n = {len(u)} and {len(t)} episodes)")
    return "\n".join(lines)


def table_4_2(runs):
    rows, csv = [], []
    for metric in ["delay", "waiting", "reward"]:
        res = {}
        for net in NETWORKS:
            ft = series(emissions_run(net, "fixed"), metric)
            idqn = converged_values(runs[(net, "A")], metric)
            res[net] = (ft, idqn, mann_whitney(idqn, ft))
        p_holm = holm([res[n][2]["p"] for n in NETWORKS])
        for (net, (ft, idqn, test)), ph in zip(res.items(), p_holm):
            def q(v):
                # quartiles with numpy's default (linear) method; whole numbers for values of 100 and more
                d = 0 if abs(np.median(v)) >= 100 else 1
                return f"{fmt(np.median(v), d)} [{fmt(np.percentile(v, 25), d)}, {fmt(np.percentile(v, 75), d)}]"
            change = relative_change(np.median(idqn), np.median(ft))
            rows.append((net, metric, [f"{NETWORKS[net]}: {metric}{UNITS[metric]}", q(ft), q(idqn),
                                       fmt(change, 1, sign=True, pct=True), fmt_p(ph), fmt(test["r"], 2, sign=True)]))
            csv.append([net, metric, len(ft), np.median(ft), np.percentile(ft, 25), np.percentile(ft, 75),
                        len(idqn), np.median(idqn), np.percentile(idqn, 25), np.percentile(idqn, 75),
                        change, test["U"], test["p"], ph, test["r"]])
    order = {"delay": 0, "waiting": 1, "reward": 2}
    rows.sort(key=lambda r: (list(NETWORKS).index(r[0]), order[r[1]]))
    save_csv("table_4_2_h1", ["network", "metric", "n_fixed", "fixed_median", "fixed_q1", "fixed_q3",
                              "n_idqn", "idqn_median", "idqn_q1", "idqn_q3", "change", "U", "p_raw",
                              "p_holm", "r"], csv)
    header = ["Network / metric", "Fixed-Time, median [IQR]", "IDQN, median [IQR]", "Change", "Holm p", "r"]
    return markdown_table(header, [r[2] for r in rows])


def spread_and_maxpressure(runs):
    lines = []
    for net, label in NETWORKS.items():
        conv = np.sort(converged_values(runs[(net, "A")], "delay"))
        ft = series(emissions_run(net, "fixed"), "delay")
        lines.append(f"- {label}: converged delays of the 21 standard-state runs, sorted: "
                     + ", ".join(fmt(v, 1) for v in conv)
                     + f"; runs worse than the Fixed-Time median ({fmt(np.median(ft), 1)} s): {int((conv > np.median(ft)).sum())}")
    for net, label in NETWORKS.items():
        ft = np.median(series(emissions_run(net, "fixed"), "delay"))
        for arm in "AB":
            med = np.median(np.vstack([series(p, "delay") for p in runs[(net, arm)]]), axis=0)
            below = med < ft
            stays = next(i + 1 for i in range(len(med)) if below[i:].all())
            lines.append(f"- {label}, arm {arm}: the median delay across the 21 runs first falls below the Fixed-Time "
                         f"median at episode {int(np.argmax(below)) + 1} and stays below from episode {stays}")
    mp = series(single_run(MAXPRESSURE_INGOLSTADT1), "reward")
    idqn = series(single_run(IDQN_200_INGOLSTADT1), "reward")
    lines.append(f"- Ingolstadt1 development runs, mean reward of the final 20 logged episodes: "
                 f"Max-Pressure {fmt(mp[-20:].mean(), 1)} ({len(mp)} episodes logged, 100-episode run), "
                 f"standard-state IDQN {fmt(idqn[-20:].mean(), 1)} ({len(idqn)} logged, 200-episode run)")
    return "\n".join(lines)


def figure_4_1(runs, plt):
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.75))
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.27, wspace=0.18)
    for ax, (net, label) in zip(axes, NETWORKS.items()):
        for arm, color, name in [("A", BLUE, "Standard state (Arm A)"), ("B", ORANGE, "Classification-aware (Arm B)")]:
            curves = np.vstack([series(p, "delay") for p in runs[(net, arm)]])
            ep = np.arange(1, curves.shape[1] + 1)
            q1, med, q3 = np.percentile(curves, [25, 50, 75], axis=0)
            ax.fill_between(ep, q1, q3, color=color, alpha=0.18, lw=0)
            ax.plot(ep, med, color=color, lw=1.2, label=name)
        ft = np.median(series(emissions_run(net, "fixed"), "delay"))
        ax.axhline(ft, color=GRAY, ls="--", lw=1.1, label="Fixed-Time (median)")
        ax.axvline(EPSILON_END, color="#666", ls=":", lw=1)
        ax.set_ylim(0, 100 if net == "cologne1" else 50)
        ax.set_title(label)
        ax.set_xlabel("Training episode")
        if net == "cologne1":
            ax.set_ylabel("Average delay per vehicle (s)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
    fig.savefig(FIGURES / "Figure_4_1_learning_curves.png")
    plt.close(fig)


def figure_4_2(runs, plt):
    rng = np.random.default_rng(SEED)
    fig = plt.figure(figsize=(6.3, 3.3))
    gs = fig.add_gridspec(1, 5, width_ratios=[2.3, 0.85, 0.55, 2.3, 0.85], wspace=0.08,
                          left=0.09, right=0.93, bottom=0.17, top=0.88)
    spec = {"cologne1": dict(main=gs[0], zoom=gs[1], ylim=(0, 95), zlim=(25.5, 43), frame=(27, 43)),
            "ingolstadt1": dict(main=gs[3], zoom=gs[4], ylim=(0, 34), zlim=(14.4, 16.0), frame=(14.2, 16.2))}
    for net, label in NETWORKS.items():
        sp = spec[net]
        ax, az = fig.add_subplot(sp["main"]), fig.add_subplot(sp["zoom"])
        ft = series(emissions_run(net, "fixed"), "delay")
        q = converged_values(runs[(net, "A")], "delay")
        top = sp["ylim"][1]
        box_with_points(ax, 0, ft, GRAY, rng, size=6)
        box_with_points(ax, 1, q, BLUE, rng)
        ax.set_ylim(*sp["ylim"]); ax.set_xlim(-0.6, 1.6)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Fixed-Time\n(100 ep.)", "IDQN\n(21 runs)"])
        ax.set_title(label, loc="left", fontweight="bold")
        if net == "cologne1":
            ax.set_ylabel("Average delay per vehicle (s)")
        m0, m1 = np.median(ft), np.median(q)
        ax.annotate("", xy=(0.5, m1 + 1.5 * top / 95), xytext=(0.5, m0), arrowprops=dict(arrowstyle="->", lw=1))
        ax.text(0.44, (m0 + m1) / 2, fmt(relative_change(m1, m0), 1, pct=True), va="center", ha="right",
                fontweight="bold", fontsize=9)
        q1_, q3_ = np.percentile(ft, [25, 75])
        whisker_top = ft[ft <= q3_ + 1.5 * (q3_ - q1_)].max()
        ax.text(0, whisker_top + 0.025 * top, f"{m0:.1f} s", va="bottom", ha="center", fontsize=8.5, fontweight="bold")
        ax.text(1, sp["frame"][0] - 0.035 * top, f"{m1:.1f} s", ha="center", va="top", color=BLUE,
                fontsize=8.5, fontweight="bold")
        ft_out = np.sort(ft[ft > top])
        if len(ft_out):
            ax.scatter([0], [top * 0.985], marker="^", color=GRAY, s=22, zorder=4, clip_on=False)
            lab = (f"{len(ft_out)} episodes\nat " + " and ".join(f"{v:.0f}" for v in ft_out) + " s"
                   if len(ft_out) > 1 else f"1 episode at {ft_out[0]:.0f} s")
            ax.text(0.1, top * 0.995, lab, ha="left", va="top", fontsize=7, color="#555", linespacing=1.1)
        for v in q[q > top]:
            ax.scatter([1], [top * 0.985], marker="^", color=BLUE, s=22, zorder=4, clip_on=False)
            ax.text(0.9, top * 0.985, f"1 run at {v:.0f} s", ha="right", va="center", fontsize=7.5, color="#555")
        f0, f1 = sp["frame"]
        ax.add_patch(Rectangle((0.66, f0), 0.68, f1 - f0, fill=False, ls="--", lw=0.8, ec="#555", zorder=5))
        box_with_points(az, 0, q, BLUE, rng, width=0.55, jitter=0.15)
        az.set_ylim(*sp["zlim"]); az.set_xlim(-0.6, 0.6)
        az.set_xticks([0]); az.set_xticklabels(["IDQN\nzoom"])
        az.yaxis.tick_right(); az.spines["left"].set_visible(False)
        az.spines["right"].set_visible(True); az.spines["right"].set_color("#777")
        az.tick_params(axis="y", labelsize=7.5)
        n_out = int((q > sp["zlim"][1]).sum() + (q < sp["zlim"][0]).sum())
        if n_out:
            az.text(0, sp["zlim"][0] + 0.01 * (sp["zlim"][1] - sp["zlim"][0]), f"{n_out} unstable\nruns outside",
                    ha="center", va="bottom", fontsize=6.8, color="#555")
        for ya, yz in [(f1, sp["zlim"][1]), (f0, sp["zlim"][0])]:
            fig.add_artist(ConnectionPatch(xyA=(1.34, ya), coordsA=ax.transData, xyB=(-0.6, yz),
                                           coordsB=az.transData, ls="--", lw=0.7, color="#777"))
    fig.savefig(FIGURES / "Figure_4_2_h1_delay.png")
    plt.close(fig)


def main():
    plt = plot_style()
    runs = training_runs("multiseed21")
    figure_4_1(runs, plt)
    figure_4_2(runs, plt)
    return "\n\n".join([
        "## Section 4.1: benchmark comparison and injection check",
        "### Table 4.1",
        table_4_1(runs),
        "Best episode: lowest-delay episode of each standard-state run, averaged over the 21 runs.",
        "### Effect of the injection on Fixed-Time (Cologne1)",
        injection_check(),
        "## Section 4.2: H1",
        "### Table 4.2",
        table_4_2(runs),
        "### Spread of the converged delays, learning curves and Max-Pressure",
        spread_and_maxpressure(runs),
        "Figures: `Figure_4_1_learning_curves.png`, `Figure_4_2_h1_delay.png`.",
    ])


if __name__ == "__main__":
    print_utf8(main())
