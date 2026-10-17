"""
Shared helpers for the thesis analysis.

Every number reported in Chapters 3 and 4 and in the appendices is computed
from files that are already in this repository:

    RESCO/results/multiseed21/   84 training runs, 21 per network and state, 200 episodes each
    RESCO/results/multiseed/     the first 6 runs per condition (24 runs), used for the six-run test
    RESCO/results/emissions/     the four CO2 validation runs (Fixed-Time 100 episodes, IDQN 200 episodes)
    RESCO/results/*.json         single development runs (Appendices A and B)
    docs/                        KBA, Destatis and Stadt Koeln data for the national estimate

RESCO stores one JSON file per run. Each metric is a dict with a single key
(the run's uuid) that maps to a list with one value per episode. RESCO logs
one value fewer than the number of training episodes (199 for a 200-episode
run, 99 for a 100-episode run), except in the emissions runs, where the IDQN
runs log all 200 episodes.
"""
from pathlib import Path
import json
import sys

import numpy as np
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "RESCO" / "results"
DOCS = ROOT / "docs"
OUT = Path(__file__).resolve().parent / "output"
TABLES = OUT / "tables"
FIGURES = OUT / "figures"

NETWORKS = {"cologne1": "Cologne1", "ingolstadt1": "Ingolstadt1"}
ARMS = {"A": "Standard (A)", "B": "Classification-aware (B)"}
# thesis name -> key in the RESCO result JSON
METRICS = {"reward": "rewards", "delay": "timeLoss", "waiting": "waitingTime"}
UNITS = {"reward": "", "delay": " (s)", "waiting": " (s)"}

CONVERGED_WINDOW = 20      # converged performance = median of the final 20 logged episodes (Section 3.5)
EPSILON_END = 160          # epsilon reaches 0 at episode 160 (Table 3.3)
BOOTSTRAP_RESAMPLES = 5000
SEED = 0                   # one fixed seed for every resampling step, so all outputs are reproducible

BLUE, ORANGE, GRAY = "#3c5a91", "#c0622f", "#8c8c8c"
MINUS = "−"


# ---------------------------------------------------------------- loading

def series(path, metric):
    """Per-episode values of one metric ('reward', 'delay', 'waiting' or a raw RESCO key)."""
    key = METRICS.get(metric, metric)
    with open(path) as f:
        data = json.load(f)
    values = data[key]
    if isinstance(values, dict):
        if len(values) != 1:
            raise ValueError(f"{path} holds {len(values)} runs, expected one")
        values = next(iter(values.values()))
    return np.asarray(values, dtype=float)


def converged(values):
    """Median of the final CONVERGED_WINDOW logged episodes."""
    return float(np.median(np.asarray(values)[-CONVERGED_WINDOW:]))


def network_of(path):
    name = Path(path).name
    for net in NETWORKS:
        if name.startswith(net):
            return net
    raise ValueError(f"unknown network in {name}")


def arm_of(path):
    return "B" if "state@drqtyped" in Path(path).name else "A"


def training_runs(folder="multiseed21"):
    """{(network, arm): [paths]} for the multi-seed runs, sorted by file name."""
    runs = {}
    for path in sorted((RESULTS / folder).glob("*.json")):
        runs.setdefault((network_of(path), arm_of(path)), []).append(path)
    return runs


def converged_values(paths, metric):
    return np.array([converged(series(p, metric)) for p in paths])


def emissions_run(network, controller):
    """Result JSON of a CO2 validation run; controller is 'fixed' or 'idqn'."""
    matches = sorted((RESULTS / "emissions").glob(f"{network}typed+{controller}_*.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one {controller} emissions run for {network}, found {matches}")
    return matches[0]


def single_run(hash_suffix, folder=""):
    """Run identified by the 16-character hash at the end of its file name.

    Development runs are searched in RESCO/results/ itself; pass folder="multiseed21" for a run of the
    multi-seed set. (Some development runs were later copied into multiseed21, so the search is not recursive.)
    """
    matches = sorted((RESULTS / folder).glob(f"*_{hash_suffix}.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"expected one run ending in {hash_suffix}, found {matches}")
    return matches[0]


# ---------------------------------------------------------------- statistics

def mann_whitney(x, y):
    """Two-sided Mann-Whitney U for x against y.

    U is the statistic of x, and the rank-biserial correlation r = 2U/(n_x n_y) - 1
    is positive when x tends to be larger than y (Kerby, 2014).
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    res = mannwhitneyu(x, y, alternative="two-sided")
    return {"U": float(res.statistic), "p": float(res.pvalue),
            "r": 2 * float(res.statistic) / (len(x) * len(y)) - 1}


def holm(pvalues):
    return list(multipletests(pvalues, method="holm")[1])


def hodges_lehmann(x, y):
    """Hodges-Lehmann estimate of the shift x - y: median of all pairwise differences."""
    return float(np.median(np.subtract.outer(np.asarray(x, float), np.asarray(y, float))))


def bootstrap_hl_ci(x, y, rng, resamples=BOOTSTRAP_RESAMPLES, level=0.95):
    """Percentile bootstrap interval of the Hodges-Lehmann shift, resampling both groups."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    stats = np.empty(resamples)
    for i in range(resamples):
        stats[i] = hodges_lehmann(rng.choice(x, len(x)), rng.choice(y, len(y)))
    tail = 100 * (1 - level) / 2
    lo, hi = np.percentile(stats, [tail, 100 - tail])
    return float(lo), float(hi)


def relative_change(new, old):
    """(new - old) / |old|; for rewards, which are negative, a positive value is an improvement."""
    return (new - old) / abs(old)


# ---------------------------------------------------------------- output

def print_utf8(text):
    """Print with UTF-8 so the typographic minus also works in a redirected Windows console."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    print(text)


def fmt(value, digits=1, sign=False, pct=False):
    """Number formatted as in the thesis: thousands separators and a typographic minus."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    v = 100 * value if pct else value
    if round(v, digits) == 0:
        v = 0.0  # no "-0.00"
    s = f"{v:+,.{digits}f}" if sign and v != 0 else f"{v:,.{digits}f}"
    s = s.replace("-", MINUS)
    return s + ("%" if pct else "")


def fmt_p(p):
    if p < 0.001:
        return "< 0.001"
    return f"{p:.4f}" if p < 0.1 else f"{p:.3f}"


def markdown_table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def save_csv(name, header, rows):
    """Write a table with full precision to output/tables/<name>.csv."""
    import csv
    TABLES.mkdir(parents=True, exist_ok=True)
    with open(TABLES / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def plot_style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
        "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "legend.fontsize": 8.5,
        "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300,
    })
    FIGURES.mkdir(parents=True, exist_ok=True)
    return plt


def box_with_points(ax, x, values, color, rng, width=0.5, jitter=0.13, size=9, alpha=0.3):
    """Box plot without fliers plus every individual value as a jittered point."""
    ax.boxplot([values], positions=[x], widths=width, whis=1.5, patch_artist=True, showfliers=False,
               medianprops=dict(color="black", lw=1.4),
               boxprops=dict(facecolor=color, alpha=alpha, edgecolor="#555", lw=0.8),
               whiskerprops=dict(lw=1), capprops=dict(lw=1))
    ax.scatter(x + rng.uniform(-jitter, jitter, len(values)), values, s=size, color=color,
               zorder=3, linewidths=0)
