#!/usr/bin/env python3
"""Recompute every headline claim of the study from the CSVs in data/.

Run it from anywhere in the repository:

    pip install pandas numpy
    python verify.py

Each line prints the claim, the value recomputed from the raw measurements, and
whether the two agree. Nothing here is hard-coded from the write-up except the
claimed value itself, which is the point: if a number in the thesis does not
come out of the data, this script says so.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

D = Path(__file__).resolve().parent / "data"
MIX = {"T1": 0.60, "T2": 0.30, "T3": 0.10}      # the stated enterprise workload
rows, failures = [], 0


def check(claim, claimed, got, tol=0.05, unit=""):
    """Compare a claimed figure with one recomputed from the data."""
    global failures
    ok = abs(got - claimed) <= tol * max(abs(claimed), 1e-9)
    failures += not ok
    rows.append((claim, f"{claimed:g}{unit}", f"{got:.4g}{unit}", "ok" if ok else "MISMATCH"))


def mixed(frame, col):
    """A per-tier mean recombined on the 60/30/10 workload."""
    t = frame.groupby("tier")[col].mean()
    return sum(MIX[k] * t[k] for k in MIX)


# ------------------------------------------------------- benchmark campaign --
bm = pd.read_csv(D / "benchmark_runs.csv")
ju = pd.read_csv(D / "judge_scores.csv")
e = {m: mixed(g, "energy_wh") for m, g in bm.groupby("model")}
lat = {m: mixed(g, "duration_s") for m, g in bm.groupby("model")}
q = ju.groupby("model").score.mean()

order = ["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b", "qwen2.5:7b"]
rows.append(("energy rises monotonically with model size", "True",
             str(all(e[a] < e[b] for a, b in zip(order, order[1:]))),
             "ok" if all(e[a] < e[b] for a, b in zip(order, order[1:])) else "MISMATCH"))

check("always-3B against always-7B, energy saved (%)", 51.6,
      100 * (1 - e["qwen2.5:3b"] / e["qwen2.5:7b"]), unit=" %")
check("always-3B against always-7B, speed-up (x)", 2.4,
      lat["qwen2.5:7b"] / lat["qwen2.5:3b"], unit="x")
check("judged quality, 7B minus 3B (5-point scale)", -0.14,
      q["qwen2.5:7b"] - q["qwen2.5:3b"], tol=0.25)
# paired prompt by prompt and averaged on the log scale, which is the basis the
# regression of Table 11 uses: the 60/30/10 mix would give a different figure
import numpy as np
pair = bm.pivot_table(index="prompt_id", columns="model", values="energy_wh", aggfunc="mean")
check("energy, 7B against 3B, paired per prompt (%)", 80.6,
      100 * (np.exp(np.log(pair["qwen2.5:7b"] / pair["qwen2.5:3b"]).mean()) - 1), unit=" %")
rows.append(("the two judges", "llama3.1:8b, qwen2.5:7b",
             ", ".join(sorted(ju.judge.unique())),
             "ok" if sorted(ju.judge.unique()) == ["llama3.1:8b", "qwen2.5:7b"] else "MISMATCH"))

# --------------------------------------------------------- cascade campaign --
cs = pd.read_csv(D / "cascade_runs.csv")
base, casc = cs[cs.pipeline == "baseline"], cs[cs.pipeline == "cascade"]
check("cascade against always-7B, energy saved (%)", 69.7,
      100 * (1 - casc.energy_wh.mean() / base.energy_wh.mean()), unit=" %")
check("cascade, latency saved (%)", 62.9,
      100 * (1 - casc.duration_s.mean() / base.duration_s.mean()), unit=" %")
check("verifier's share of cascade energy (%)", 34,
      100 * casc.energy_scorer_wh.sum() / casc.energy_wh.sum(), tol=0.06, unit=" %")
check("baseline objective accuracy (%)", 85.7,
      100 * base.objective_check.mean(), unit=" %")
check("cascade objective accuracy (%)", 57.1,
      100 * casc.objective_check.mean(), unit=" %")
accepted = casc[casc.escalations == 0]
wrong = accepted[accepted.objective_check == False]
rows.append(("verifier false accepts", "3 of 10",
             f"{len(wrong)} of {len(accepted)}",
             "ok" if (len(wrong), len(accepted)) == (3, 10) else "MISMATCH"))

# -------------------------------------------------- prompt specialisation ----
sp = pd.read_csv(D / "specialisation_runs.csv").set_index("Bras")
w = sp.groupby("Bras")["Énergie (Wh)"].mean()
check("1.5B with an output contract against 7B generic, energy saved (%)", 67,
      100 * (1 - w["A3_moyen_specialise"] / w["A4_grand_generique"]), tol=0.06, unit=" %")
check("output contract at constant size, extra energy on the 0.5B (%)", 42,
      100 * (w["A2_petit_specialise"] / w["A1_petit_generique"] - 1), tol=0.08, unit=" %")

# --------------------------------------------------- model specialisation ----
cd = pd.read_csv(D / "coder_summary.csv").set_index("arm")
check("code-trained 3B against general 7B, energy saved (%)", 50.5,
      100 * (1 - cd.loc["coder 3B", "energy_wh"] / cd.loc["general 7B", "energy_wh"]), unit=" %")
check("code-trained 3B against general 7B, latency saved (%)", 50.9,
      100 * (1 - cd.loc["coder 3B", "latency_s"] / cd.loc["general 7B", "latency_s"]), unit=" %")
rows.append(("tasks solved, coder 3B against general 7B", "14 of 20 against 13 of 20",
             f"{int(cd.loc['coder 3B','solved'])} of 20 against "
             f"{int(cd.loc['general 7B','solved'])} of 20",
             "ok" if (cd.loc["coder 3B", "solved"], cd.loc["general 7B", "solved"]) == (14, 13)
             else "MISMATCH"))

# --------------------------------------------- the local-against-cloud flip --
# published per-query energy, Jegham et al. (2025) Table 4; AWS PUE 1.14;
# the paper's "long" output of ~1,000 words taken as 1,350 tokens
PUB = {"qwen2.5:0.5b": 0.552, "qwen2.5:1.5b": 0.552,
       "qwen2.5:3b": 0.707, "qwen2.5:7b": 0.443}
tok = {m: mixed(g, "tokens_out") for m, g in bm.groupby("model")}
cloud = {m: PUB[m] / 1.14 / 1350 * tok[m] for m in PUB}
check("measured here, 0.5B energy as a share of the 7B", 0.17,
      e["qwen2.5:0.5b"] / e["qwen2.5:7b"], tol=0.06)
check("published cloud figures, 0.5B energy as a share of the 7B", 1.22,
      cloud["qwen2.5:0.5b"] / cloud["qwen2.5:7b"], tol=0.06)

# ------------------------------------------------------------------ report ---
wid = max(len(r[0]) for r in rows)
print(f"\n{'claim':{wid}}  {'stated':>26}  {'recomputed':>26}  status")
print("-" * (wid + 60))
for c, a, b, s in rows:
    print(f"{c:{wid}}  {a:>26}  {b:>26}  {s}")
print("-" * (wid + 60))
print(f"{len(rows) - failures} of {len(rows)} checks reproduce the published figure.\n")
sys.exit(1 if failures else 0)
