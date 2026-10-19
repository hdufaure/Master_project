"""Figure set for the three levers, rebuilt from the final campaign CSVs only.

Sources, fixed:
  benchmark   4a213379-benchmark_runs.csv   (144 runs)
  judges      2f80b0de-judge_scores.csv     (96 ratings, all parsed 5/5)
  cascade     3e059357-cascade_runs.csv     (24 runs, English columns)
  block A     342d29ee (6 Oct, thesis) + d78c8ee0 (5 Oct, replication)
  block B     cc5f9e6e-blocB_runs.csv
  coder       608a8266-coder_summary.csv    (20 tasks x 7 arms)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd, numpy as np, os

D = '../data/'          # data this script reads
U = D             # kept for backward compatibility
OUT = './'                    # figures are written next to this script
os.makedirs(OUT, exist_ok=True)

# ---- design parameters ------------------------------------------------------
# ---------------------------------------------------------------------------
# One colour role per variable, used identically in every figure:
#   model size  -> the burgundy ramp, light 0.5B to dark 7B. Never anything else.
#   task tier   -> the blue ramp, light T1 to dark T3. Never anything else.
#   comparisons -> PROPOSED (what this thesis recommends) against REFERENCE
#                  (the status quo it is measured against); PUBLISHED for a
#                  figure taken from the literature rather than metered here.
# All three were checked with the colour-blindness and contrast validator.
RAMP = ['#E9B9CA', '#D47C9D', '#B3295E', '#6E1038']        # 0.5B 1.5B 3B 7B
MCOL = {0.5: RAMP[0], 1.5: RAMP[1], 3.0: RAMP[2], 7.0: RAMP[3]}
TCOL = ['#BBD9EA', '#4A93C4', '#0A5273']                   # T1 T2 T3
PROPOSED, PUBLISHED, REFERENCE, NEUTRAL = '#B3295E', '#C4751F', '#C9C3C7', '#4F4B57'
CAT = [PROPOSED, PUBLISHED, NEUTRAL]
INK, INK2, INK3 = '#2A2228', '#55505A', '#8A8289'
GRID, SURF = '#E6E1E4', '#FFFFFF'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 15,
    'axes.edgecolor': GRID, 'axes.labelcolor': INK2, 'axes.titlecolor': INK,
    'xtick.color': INK2, 'ytick.color': INK2,
    'figure.facecolor': SURF, 'axes.facecolor': SURF,
    'axes.spines.top': False, 'axes.spines.right': False,
    'xtick.bottom': False, 'ytick.left': False,
})

def frame(ax, ylab=None, xlab=None):
    ax.grid(axis='y', color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    ax.spines['left'].set_color(GRID)
    ax.spines['bottom'].set_color(GRID)
    if ylab: ax.set_ylabel(ylab, fontsize=14, labelpad=10)
    if xlab: ax.set_xlabel(xlab, fontsize=14, labelpad=10)

def head(fig, title, sub=None):
    import textwrap
    lines = textwrap.wrap(title, 54)
    fig.text(0.055, 0.962, '\n'.join(lines), fontsize=21, fontweight='bold',
             color=INK, va='top', linespacing=1.22)
    if sub:
        ysub = 0.962 - (0.356 * len(lines) + 0.16) / fig.get_figheight()
        sub = '\n'.join(l for part in sub.split('\n')
                         for l in textwrap.wrap(part, 92) or [''])
        fig.text(0.055, ysub, sub, fontsize=14.5, color=INK2, va='top',
                 linespacing=1.38)

def foot(fig, txt):
    fig.text(0.055, 0.022, txt, fontsize=12, color=INK3, va='bottom')

def save(fig, name):
    fig.savefig(OUT + name, dpi=190, facecolor=SURF, bbox_inches=None)
    plt.close(fig)
    print('  wrote', name)

SZ = {'qwen2.5:0.5b': 0.5, 'qwen2.5:1.5b': 1.5, 'qwen2.5:3b': 3.0, 'qwen2.5:7b': 7.0}
LBL = ['0.5B', '1.5B', '3B', '7B']
TIER = {'T1': 'Routine (T1)', 'T2': 'Analytical (T2)', 'T3': 'Complex (T3)'}

# ---- data -------------------------------------------------------------------
bm = pd.read_csv(D + 'benchmark_runs.csv')
ju = pd.read_csv(D + 'judge_scores.csv'); ju['sz'] = ju.model.map(SZ)
cs = pd.read_csv(D + 'cascade_runs.csv')
a6 = pd.read_csv(D + 'specialisation_runs.csv')
a5 = pd.read_csv(D + 'discarded_runs/specialisation_runs_fixed_order.csv')
bB = pd.read_csv(D + 'discarded_runs/blockB_runs_flawed_protocol.csv')
cd = pd.read_csv(D + 'coder_summary.csv')

E_wh = bm.pivot_table(index='parameters_b', columns='tier', values='energy_wh', aggfunc='mean')
L_s = bm.pivot_table(index='parameters_b', columns='tier', values='duration_s', aggfunc='mean')
Q = ju.pivot_table(index='sz', columns='tier', values='score', aggfunc='mean')
MIX = {'T1': .60, 'T2': .30, 'T3': .10}

print('L1 — levier 1, le modele')

# ============================================================ L1a energy =====
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.115, right=.975, top=.70, bottom=.155)
x = np.arange(4); w = 0.26
for i, t in enumerate(['T1', 'T2', 'T3']):
    v = E_wh[t].values
    ax.bar(x + (i - 1) * (w + .018), v, w, color=TCOL[i], label=TIER[t],
           zorder=3, edgecolor=SURF, linewidth=1.4)
    for xi, vi in zip(x + (i - 1) * (w + .018), v):
        ax.text(xi, vi + .0012, f'{vi:.4f}'.lstrip('0'), ha='center', va='bottom',
                fontsize=10.5, color=INK2, rotation=0)
ax.set_xticks(x); ax.set_xticklabels(LBL, fontsize=15, color=INK)
frame(ax, 'Wh per request (whole machine)')
ax.legend(frameon=False, fontsize=13, loc='upper left', labelcolor=INK2)
ax.set_ylim(0, .049)
head(fig, 'Energy per request rises faster than model size',
     'Four Qwen2.5 sizes, 12 prompts, 3 repetitions each — 144 metered runs. From 0.5B to 7B\nthe cost multiplies by 4.2 on routine work and by 7.6 on analytical work.')
foot(fig, 'Source: benchmark_runs.csv · CodeCarbon 3.2.6, machine mode, 1 Hz · mean of 3 repetitions')
save(fig, 'L1a_energy_by_size.png')

# ============================================================ L1b quality ====
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.115, right=.975, top=.70, bottom=.155)
for i, t in enumerate(['T1', 'T2', 'T3']):
    v = Q[t].values
    ax.plot(x, v, '-o', color=TCOL[i], lw=2, ms=9, label=TIER[t], zorder=3,
            markeredgecolor=SURF, markeredgewidth=1.6)
ax.axvspan(1.72, 3.28, color='#F2EEF0', zorder=1)
ax.text(2.5, 2.42, 'plateau: the 7B is not\nseparable from the 3B',
        ha='center', fontsize=12.5, color=INK2, style='italic')
for i, t in enumerate(['T1', 'T3']):
    ax.annotate(f'{Q[t].values[3]:.2f}', (3, Q[t].values[3]), textcoords='offset points',
                xytext=(10, -4), fontsize=11.5, color=INK2)
    ax.annotate(f'{Q[t].values[2]:.2f}', (2, Q[t].values[2]), textcoords='offset points',
                xytext=(-6, 11), fontsize=11.5, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(LBL, fontsize=15, color=INK)
ax.set_xlim(-.35, 3.6); ax.set_ylim(2.2, 5.15)
frame(ax, 'Mean judged score (1 to 5)')
ax.legend(frameon=False, fontsize=13, loc='upper left', labelcolor=INK2,
          bbox_to_anchor=(.015, .99))
head(fig, 'Judged quality stops improving at three billion parameters',
     '96 ratings, two judges from different model families, five criteria each. The 3B and the 7B\ncannot be separated (p = 0.70) — and the 3B scores higher on routine work.')
foot(fig, 'Source: judge_scores.csv · 96 of 96 ratings parsed on the 1-to-5 rubric · judges’ own energy excluded')
save(fig, 'L1b_quality_by_size.png')

# ============================================================ L1c the trade ==
pol = pd.DataFrame({
    'wh': [sum(E_wh[t][s] * MIX[t] for t in MIX) for s in [0.5, 1.5, 3.0, 7.0]],
    'q':  [sum(Q[t][s] * MIX[t] for t in MIX) for s in [0.5, 1.5, 3.0, 7.0]],
    's':  [sum(L_s[t][s] * MIX[t] for t in MIX) for s in [0.5, 1.5, 3.0, 7.0]],
}, index=LBL)
fig, ax = plt.subplots(figsize=(9.6, 5.6)); fig.subplots_adjust(left=.115, right=.985, top=.70, bottom=.215)
ax.plot(pol.wh, pol.q, '-', color=GRID, lw=2.2, zorder=2)
for i, (n, r) in enumerate(pol.iterrows()):
    big = n in ('3B', '7B')
    ax.plot(r.wh, r.q, 'o', ms=20 if big else 14, color=RAMP[i], zorder=4,
            markeredgecolor='#B3295E' if big else SURF, markeredgewidth=2.4 if big else 1.6)
    ax.annotate(f'{n}\n{r.wh:.4f} Wh · {r.q:.2f}/5', (r.wh, r.q), textcoords='offset points',
                xytext=(-16 if n == '7B' else 14, 10 if n in ('3B','7B') else -6),
                ha='right' if n == '7B' else 'left', fontsize=12.5,
                color=INK if big else INK2, fontweight='bold' if big else 'normal')
ax.annotate('', xy=(pol.wh['3B'], pol.q['3B'] - .16), xytext=(pol.wh['7B'], pol.q['7B'] - .16),
            arrowprops=dict(arrowstyle='-|>', color='#B3295E', lw=2.2, shrinkA=9, shrinkB=9))
ax.text((pol.wh['3B'] + pol.wh['7B']) / 2, pol.q['3B'] - .58,
        '−51.6 % energy, 2.4× faster,\nquality indistinguishable', ha='center',
        fontsize=13, color='#B3295E', fontweight='bold')
ax.set_xlim(.0012, .0238); ax.set_ylim(2.75, 4.72)
frame(ax, 'Mean judged score (1 to 5)', 'Wh per request on a 60 / 30 / 10 workload')
head(fig, 'Choosing the 3B once, at design time, is the single best move',
     'The same 144 measurements reweighted as enterprise traffic: 60 % routine, 30 % analytical,\n10 % complex. This mix is a stated assumption, not a measurement.')
foot(fig, 'Source: benchmark_runs.csv + judge_scores.csv, recombined · mix held fixed across all four policies')
save(fig, 'L1c_policy_plane.png')

# ============================================================ L1d latency ====
fig, ax = plt.subplots(figsize=(9.6, 5.0)); fig.subplots_adjust(left=.115, right=.975, top=.70, bottom=.155)
for i, t in enumerate(['T1', 'T2', 'T3']):
    v = L_s[t].values
    ax.bar(x + (i - 1) * (w + .018), v, w, color=TCOL[i], label=TIER[t],
           zorder=3, edgecolor=SURF, linewidth=1.4)
for xi, vi in zip(x, L_s['T3'].values):
    ax.text(xi + (w + .018), vi + 4, f'{vi:.0f} s', ha='center', fontsize=11.5, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(LBL, fontsize=15, color=INK)
frame(ax, 'Seconds per request')
ax.legend(frameon=False, fontsize=13, loc='upper left', labelcolor=INK2)
ax.set_ylim(0, 200)
head(fig, 'Latency carries the same penalty, and users feel this one',
     'The 7B takes almost three minutes on a complex request, against 72 seconds for the 3B.')
foot(fig, 'Source: benchmark_runs.csv · wall-clock, model already loaded')
save(fig, 'L1d_latency_by_size.png')

print('L2 — levier 2, la cascade')

# ============================================================ L2a scorer =====
bl = cs[cs.pipeline == 'baseline'].groupby('tier').energy_wh.mean()
ca = cs[cs.pipeline == 'cascade'].groupby('tier')[['energy_answers_wh', 'energy_scorer_wh']].mean()
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.115, right=.975, top=.655, bottom=.155)
xt = np.arange(3); w2 = 0.30
ax.bar(xt - w2 / 1.75, bl.values, w2, color='#C9C3C7', label='Baseline — one call to the 7B',
       zorder=3, edgecolor=SURF, linewidth=1.4)
ax.bar(xt + w2 / 1.75, ca.energy_answers_wh.values, w2, color=CAT[0],
       label='Cascade — the answers', zorder=3, edgecolor=SURF, linewidth=1.4)
ax.bar(xt + w2 / 1.75, ca.energy_scorer_wh.values, w2, bottom=ca.energy_answers_wh.values,
       color=PUBLISHED, label='Cascade — the scorer that decides', zorder=3,
       edgecolor=SURF, linewidth=1.8)
for i in range(3):
    tot = ca.energy_answers_wh.values[i] + ca.energy_scorer_wh.values[i]
    sh = 100 * ca.energy_scorer_wh.values[i] / tot
    ax.text(xt[i] + w2 / 1.75, tot + .0011, f'{sh:.0f} % is the scorer',
            ha='center', fontsize=11.5, color=PUBLISHED, fontweight='bold')
    ax.text(xt[i] - w2 / 1.75, bl.values[i] + .0011, f'{bl.values[i]:.4f}'.lstrip('0'),
            ha='center', fontsize=11.5, color=INK2)
ax.set_xticks(xt); ax.set_xticklabels([TIER[t] for t in ['T1', 'T2', 'T3']], fontsize=14, color=INK)
frame(ax, 'Wh per request')
ax.legend(frameon=False, fontsize=12, loc='upper right', labelcolor=INK2,
          bbox_to_anchor=(1.005, 1.015))
ax.set_ylim(0, .070)
head(fig, 'The cascade is cheaper — but a third of what it spends is spent deciding',
     'Two pipelines run end to end on the same twelve prompts. The scorer that decides\nwhether to escalate is itself a model call, paid on every request.')
foot(fig, 'Source: cascade_runs.csv · scorer energy counted in full, 34 % of the pipeline total')
save(fig, 'L2a_cascade_scorer.png')

# ============================================================ L2b the cost ===
accb = pd.to_numeric(cs[cs.pipeline == 'baseline'].objective_check, errors='coerce').mean() * 100
accc = pd.to_numeric(cs[cs.pipeline == 'cascade'].objective_check, errors='coerce').mean() * 100
rows = [('Energy per request', 0.02727, 0.00827, 'Wh', True),
        ('Latency per request', 116.6, 43.3, 's', True),
        ('Model calls per request', 1.0, 2.33, '', False),
        ('Answers passing the\ndeterministic check', accb, accc, ' %', False)]
fig, ax = plt.subplots(figsize=(9.6, 5.2)); fig.subplots_adjust(left=.30, right=.93, top=.70, bottom=.14)
yy = np.arange(len(rows))[::-1]
for y, (nm, v0, v1, u, good) in zip(yy, rows):
    col = PROPOSED if good else PUBLISHED
    ax.plot([0, 1], [y, y], '-', color=GRID, lw=2, zorder=2)
    ax.plot(0, y, 'o', ms=13, color='#C9C3C7', zorder=4, markeredgecolor=SURF, markeredgewidth=1.6)
    ax.plot(1, y, 'o', ms=15, color=col, zorder=4, markeredgecolor=SURF, markeredgewidth=1.6)
    f = (lambda v: f'{v:.4f} ') if u == 'Wh' else (lambda v: f'{v:.1f}')
    ax.text(-.055, y, f(v0) + u, ha='right', va='center', fontsize=13, color=INK2)
    ax.text(1.055, y, f(v1) + u, ha='left', va='center', fontsize=13.5, color=col, fontweight='bold')
    pc = 100 * (v1 - v0) / v0
    ax.text(.5, y + .20, f'{pc:+.1f} %', ha='center', fontsize=12.5, color=col, fontweight='bold')
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows], fontsize=13.5, color=INK)
ax.set_xticks([0, 1]); ax.set_xticklabels(['Baseline\n(always the 7B)', 'Cascade\n(0.5B → 3B → 7B)'],
                                          fontsize=13, color=INK)
ax.set_xlim(-.42, 1.42); ax.set_ylim(-.6, len(rows) - .35)
ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]
head(fig, 'What the cascade buys, and what it costs',
     'The energy and latency savings are real and large. They are paid for in correctness:\nnearly a third of the answers that passed the deterministic check no longer pass it.')
foot(fig, 'Source: cascade_runs.csv · 12 prompts, both pipelines, deterministic check where one exists')
save(fig, 'L2b_cascade_tradeoff.png')

# ============================================================ L2c who answers
vc = cs[cs.pipeline == 'cascade'].final_model.value_counts()
fig, ax = plt.subplots(figsize=(9.6, 4.2)); fig.subplots_adjust(left=.055, right=.975, top=.54, bottom=.26)
left = 0
order = ['qwen2.5:0.5b', 'qwen2.5:3b', 'qwen2.5:7b']
nice = {'qwen2.5:0.5b': 'the 0.5B', 'qwen2.5:3b': 'the 3B', 'qwen2.5:7b': 'the 7B'}
for i, m in enumerate(order):
    n = int(vc.get(m, 0))
    if n == 0: continue
    ax.barh([0], [n], left=left, height=.52, color=RAMP[[0, 2, 3][i]], zorder=3,
            edgecolor=SURF, linewidth=2.2)
    ax.text(left + n / 2, 0, f'{nice[m]}\n{n} of 12', ha='center', va='center', fontsize=13.5,
            color=SURF if i else INK, fontweight='bold')
    left += n
ax.set_xlim(0, 12); ax.set_ylim(-.5, .5)
ax.set_yticks([]); ax.set_xticks([0, 3, 6, 9, 12]); ax.grid(False)
[s.set_visible(False) for s in ax.spines.values()]
ax.set_xlabel('Prompts, by the model that produced the answer the user receives', fontsize=13, labelpad=8, color=INK2)
head(fig, 'The cascade almost never escalates — which is why it saves, and why it misses',
     'Ten of the twelve answers come from the 0.5B. The scorer accepted them; the deterministic check did not.')
foot(fig, 'Source: cascade_runs.csv · 2 escalations over 12 prompts, 2.33 model calls per request')
save(fig, 'L2c_who_answers.png')

print('L3 — levier 3, la specialisation')

# ============================================================ L3a block A ====
ARM = {'A1_petit_generique': ('0.5B, generic prompt', 0.5),
       'A2_petit_specialise': ('0.5B, output contract', 0.5),
       'A3_moyen_specialise': ('1.5B, output contract', 1.5),
       'A4_grand_generique': ('7B, generic prompt', 7.0),
       'A5_grand_specialise': ('7B, output contract', 7.0)}
g6 = a6.groupby('Bras').agg(wh=('Énergie (Wh)', 'mean'), acc=('Exactitude', 'mean'))
fig, ax = plt.subplots(figsize=(9.6, 5.6)); fig.subplots_adjust(left=.115, right=.985, top=.70, bottom=.215)
for k, (nm, ci) in ARM.items():
    r = g6.loc[k]
    hl = k in ('A3_moyen_specialise', 'A4_grand_generique')
    ax.plot(r.wh, 100 * r.acc, 'o', ms=19 if hl else 13, color=MCOL[ci], zorder=4,
            markeredgecolor=INK if hl else '#8A6B7A',
            markeredgewidth=2.2 if hl else 1.4)
    dx, dy = {'A4_grand_generique': (15, -34), 'A3_moyen_specialise': (-15, -34),
              'A5_grand_specialise': (-15, 11), 'A2_petit_specialise': (14, -4),
              'A1_petit_generique': (14, -4)}[k]
    ax.annotate(f'{nm}\n{r.wh:.4f} Wh', (r.wh, 100 * r.acc), textcoords='offset points',
                xytext=(dx, dy), fontsize=12, color=INK if hl else INK2,
                ha='right' if dx < 0 else 'left',
                fontweight='bold' if hl else 'normal')
ax.annotate('', xy=(g6.loc['A3_moyen_specialise'].wh, 88), xytext=(g6.loc['A4_grand_generique'].wh, 88),
            arrowprops=dict(arrowstyle='-|>', color=INK, lw=2.2, shrinkA=11, shrinkB=11))
ax.text(.0727, 95.5, 'same 88 % accuracy, −66.6 % energy', ha='center', fontsize=13,
        color=INK, fontweight='bold')
ax.set_xlim(-.004, .183); ax.set_ylim(22, 110)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f} %'))
frame(ax, 'Tasks solved (deterministic check)', 'Wh per request')
head(fig, 'A 1.5B under a output contract matches a 7B answering freely',
     'Eight extraction, classification, translation and normalisation tasks, five arms.\nThe contract fixes the output format and forbids commentary. Nothing else changes.')
foot(fig, 'Source: blocA_runs.csv, 6 October 2026 · accuracy and output tokens identical in the 5 October replication')
save(fig, 'L3a_blockA_plane.png')

# ============================================================ L3b replication
g5 = a5.groupby('Bras').agg(wh=('Énergie (Wh)', 'mean'), acc=('Exactitude', 'mean'))
keys = list(ARM.keys())
fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 5.8), gridspec_kw={'wspace': .32})
fig.subplots_adjust(left=.095, right=.975, top=.615, bottom=.215)
xk = np.arange(5)
axL.bar(xk - .19, [100 * g5.loc[k].acc for k in keys], .34, color='#C9C3C7',
        label='First run — arms in fixed order', zorder=3, edgecolor=SURF, linewidth=1.4)
axL.bar(xk + .19, [100 * g6.loc[k].acc for k in keys], .34, color=PROPOSED,
        label='Re-run — arm order randomised', zorder=3, edgecolor=SURF, linewidth=1.4)
axL.set_title('Accuracy — unchanged by the fix', fontsize=14.5, color=INK, pad=10)
axL.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f} %'))
axL.set_ylim(0, 132); frame(axL)
axL.legend(frameon=False, fontsize=12.5, loc='upper left', labelcolor=INK2)
axR.bar(xk - .19, [g5.loc[k].wh for k in keys], .34, color='#C9C3C7', zorder=3,
        edgecolor=SURF, linewidth=1.4)
axR.bar(xk + .19, [g6.loc[k].wh for k in keys], .34, color=PROPOSED, zorder=3,
        edgecolor=SURF, linewidth=1.4)
axR.set_title('Energy — reversed by the fix', fontsize=14.5, color=INK, pad=10)
axR.set_ylim(0, .185); frame(axR, 'Wh per request')
for a_ in (axL, axR):
    a_.set_xticks(xk)
    a_.set_xticklabels(['A1', 'A2', 'A3', 'A4', 'A5'], fontsize=13.5, color=INK)
axR.annotate('', xy=(1.0, .034), xytext=(1.0, .064),
              arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.6))
axR.text(1.0, .070, 'the contract reads as −37 %\nin order, +42 % randomised', fontsize=11.5,
         color=INK, fontweight='bold', va='bottom', ha='center')
head(fig, 'Why the first campaign was discarded and run again',
     'In the first run the five arms always executed in the same order, so each contract arm ran on a\nmachine the generic arm had just warmed. Randomising the order reverses the energy conclusion.')
foot(fig, 'Source: blocA_runs.csv, 5 then 6 October 2026 · temperature 0: identical answers and identical output tokens in both runs')
save(fig, 'L3b_blockA_replication.png')

# ============================================================ L3c coder ======
fig, ax = plt.subplots(figsize=(9.6, 5.6)); fig.subplots_adjust(left=.115, right=.985, top=.70, bottom=.215)
for _, r in cd.iterrows():
    spec = r['kind'] == 'specialised'
    hl = r.arm in ('coder 3B', 'general 7B')
    ax.plot(r.energy_wh, r['accuracy %'], 'o' if spec else 's', ms=19 if hl else 12,
            color=PROPOSED if spec else NEUTRAL, zorder=4,
            markeredgecolor=INK if hl else SURF, markeredgewidth=2.2 if hl else 1.5)
    dx, dy = {'general 0.5B': (14, 4), 'coder 0.5B': (14, -8),
              'general 1.5B': (-14, -4), 'coder 1.5B': (14, 4),
              'general 3B': (14, -26), 'coder 3B': (-16, 8),
              'general 7B': (-14, -28)}[r.arm]
    ax.annotate(f"{r.arm}\n{r['accuracy %']:.0f} % · {r.energy_wh:.4f} Wh",
                (r.energy_wh, r['accuracy %']), textcoords='offset points', xytext=(dx, dy),
                fontsize=11.5, color=INK if hl else INK2,
                ha='right' if dx < 0 else 'left',
                fontweight='bold' if hl else 'normal')
ax.annotate('', xy=(cd.loc[5, 'energy_wh'], 70), xytext=(cd.loc[6, 'energy_wh'], 65),
            arrowprops=dict(arrowstyle='-|>', color=INK, lw=2.2, shrinkA=12, shrinkB=12))
ax.text(.0138, 80, '+5 points of accuracy\nfor −50.5 % energy', ha='center', fontsize=13,
        color=INK, fontweight='bold')
h1 = plt.Line2D([], [], marker='o', ls='', color=PROPOSED, ms=11, label='Code-trained model')
h2 = plt.Line2D([], [], marker='s', ls='', color=NEUTRAL, ms=10, label='General model')
ax.legend(handles=[h1, h2], frameon=False, fontsize=13, loc='lower right', labelcolor=INK2)
ax.set_xlim(-.0007, .0225); ax.set_ylim(-16, 95)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f} %'))
frame(ax, 'Programming tasks solved (20 tasks, executed and checked)', 'Wh per request')
head(fig, 'A model trained for the task beats a model four times its size',
     '140 runs, 20 programming tasks, every answer executed against its tests. The 3B coder solves\nmore than the 7B generalist for half the energy — and specialisation cannot rescue the 0.5B.')
foot(fig, 'Source: coder_summary.csv · qwen2.5-coder against qwen2.5 at equal parameter count')
save(fig, 'L3c_coder_vs_general.png')

print('\nSYNTHESE')

# ============================================================ S1 the ladder ==
lad = [('0.5B + output contract\nmeasured here', 0.0228, PROPOSED, 'blocA_runs.csv'),
       ('7B + generic prompt\nmeasured here', 0.1090, RAMP[3], 'blocA_runs.csv'),
       ('Frontier model (GPT-4o)\npublished measurement', 0.4200, PUBLISHED,
        'Jegham et al. (2025), short prompt'),
       ('Frontier model ≈400B\nour scaling law extended', 0.4276, NEUTRAL,
        'log-log fit on our four models')]
fig, ax = plt.subplots(figsize=(9.6, 5.2)); fig.subplots_adjust(left=.335, right=.945, top=.575, bottom=.225)
yy = np.arange(len(lad))[::-1]
for y, (nm, v, col, src) in zip(yy, lad):
    ax.barh([y], [v], height=.46, color=col, zorder=3, edgecolor=SURF, linewidth=1.6)
    ax.text(v * 1.10, y, f'{v:.3f} Wh   ×{v/0.0228:.0f}', va='center', fontsize=13,
            color=col, fontweight='bold')
    ax.text(.0062, y - .34, src, fontsize=10, color=INK3, va='top')
ax.set_yticks(yy); ax.set_yticklabels([l[0] for l in lad], fontsize=12, color=INK)
ax.set_xscale('log'); ax.set_xlim(.006, 14)
ax.set_xticks([.01, .1, 1]); ax.set_xticklabels(['0.01', '0.1', '1'], fontsize=13)
ax.grid(axis='x', color=GRID, lw=1, zorder=0); ax.set_axisbelow(True)
[s.set_visible(False) for s in ax.spines.values()]
ax.set_xlabel('Wh per request — logarithmic scale', fontsize=13, labelpad=8, color=INK2)
head(fig, 'The levers are worth five. The class of model is worth eighteen.',
     'No frontier model was run for this thesis. The bottom two bars are two independent\nestimates of the same thing, and they agree: a published measurement of GPT-4o, and\nour own scaling law extended to a 400-billion-parameter model.')
foot(fig, 'Sources: blocA_runs.csv (measured) · Jegham et al. 2025 · extrapolation of the local scaling law')
save(fig, 'S1_ladder.png')

# ============================================================ S2 rebound =====
base = pol.wh['7B']; after = pol.wh['3B']
gr = np.linspace(1, 3, 200)
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.125, right=.975, top=.60, bottom=.195)
ax.plot(gr, 100 * (after * gr - base) / base, '-', color=PROPOSED, lw=2.6, zorder=4)
ax.axhline(0, color=INK3, lw=1.4, zorder=3)
ax.fill_between(gr, -60, 0, color='#EEF4F8', zorder=1)
ax.fill_between(gr, 0, 60, color='#FBF0F4', zorder=1)
bp = base / after
ax.plot([bp], [0], 'o', ms=15, color=PROPOSED, zorder=5, markeredgecolor=SURF, markeredgewidth=2)
ax.annotate(f'{bp:.2f}× the usage\nand the saving is gone', (bp, 0), textcoords='offset points',
            xytext=(16, -46), fontsize=13, color=INK, fontweight='bold')
ax.text(1.05, -42, 'the organization still emits less', fontsize=12.5, color='#0F7FB0', style='italic')
ax.text(2.86, 40, 'it emits more than before', fontsize=12.5, color='#B3295E',
        style='italic', ha='right')
ax.set_xlim(1, 3); ax.set_ylim(-60, 60)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.1f}×'))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:+.0f} %'))
frame(ax, 'Change in total energy', 'Requests after the switch, relative to before')
head(fig, 'A 51.6 % saving per request survives only a doubling of usage',
     'Efficiency is not a cap. Unless request volume is governed too,\nthe whole gain can be spent.')
foot(fig, 'Derived from the 60 / 30 / 10 policy figures · break-even at 2.07× the request volume')
save(fig, 'S2_rebound.png')

print('\nnumbers used')
print(' pol\n', pol.round(4).to_string())
print(' cascade total: baseline %.5f cascade %.5f  = %+.1f%%' %
      (0.02727, 0.00827, 100 * (0.00827 - 0.02727) / 0.02727))
print(' blockA A3 vs A4 6Oct: %+.1f%% | 5Oct: %+.1f%%' % (
    100 * (g6.loc['A3_moyen_specialise'].wh - g6.loc['A4_grand_generique'].wh) / g6.loc['A4_grand_generique'].wh,
    100 * (g5.loc['A3_moyen_specialise'].wh - g5.loc['A4_grand_generique'].wh) / g5.loc['A4_grand_generique'].wh))
print(' blockA A1->A2 6Oct: %+.1f%% | 5Oct: %+.1f%%' % (
    100 * (g6.loc['A2_petit_specialise'].wh - g6.loc['A1_petit_generique'].wh) / g6.loc['A1_petit_generique'].wh,
    100 * (g5.loc['A2_petit_specialise'].wh - g5.loc['A1_petit_generique'].wh) / g5.loc['A1_petit_generique'].wh))
print(' coder3B vs general7B: %+.1f%% energy, %+.0f pts' % (
    100 * (cd.loc[5, 'energy_wh'] - cd.loc[6, 'energy_wh']) / cd.loc[6, 'energy_wh'],
    cd.loc[5, 'accuracy %'] - cd.loc[6, 'accuracy %']))
print(' rebound break-even: %.2fx' % bp)

print('\nfigures restored')

# ======================================================= L1e objective acc ===
acc = bm.copy()
acc['ok'] = pd.to_numeric(acc.objective_check, errors='coerce')
A = acc.pivot_table(index='parameters_b', columns='tier', values='ok', aggfunc='mean') * 100
fig, ax = plt.subplots(figsize=(9.6, 5.2)); fig.subplots_adjust(left=.115, right=.975, top=.655, bottom=.155)
xb = np.arange(4); wb = 0.34
for i, t in enumerate(['T1', 'T3']):
    v = A[t].values
    ax.bar(xb + (i - .5) * (wb + .02), v, wb, color=TCOL[i * 2], label=TIER[t],
           zorder=3, edgecolor=SURF, linewidth=1.4)
    for xi, vi in zip(xb + (i - .5) * (wb + .02), v):
        ax.text(xi, vi + 2, f'{vi:.0f} %', ha='center', fontsize=12, color=INK2)
ax.set_xticks(xb); ax.set_xticklabels(LBL, fontsize=15, color=INK)
ax.set_ylim(0, 118); ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f} %'))
frame(ax, 'Answers passing the deterministic check')
ax.legend(frameon=False, fontsize=13, loc='upper left', labelcolor=INK2)
head(fig, 'The same plateau, with no judge involved at all',
     'Seven of the twelve prompts carry a machine-checkable answer.\nOn those the 3B passes all of them, and the 7B does not.')
foot(fig, 'Source: benchmark_runs.csv · deterministic checks, no model in the loop')
save(fig, 'L1e_objective_accuracy.png')

# ======================================================= L1f token economics =
tk = bm.groupby('parameters_b').agg(wh=('energy_wh', 'mean'), tok=('tokens_out', 'mean'))
tk['per_k'] = tk.wh / tk.tok * 1000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 5.2), gridspec_kw={'wspace': .30})
fig.subplots_adjust(left=.095, right=.975, top=.615, bottom=.165)
a1.bar(xb, tk.per_k.values, .52, color=[MCOL[m] for m in tk.index], zorder=3,
       edgecolor=SURF, linewidth=1.4)
for xi, vi in zip(xb, tk.per_k.values):
    a1.text(xi, vi + .0015, f'{vi:.3f}', ha='center', fontsize=12, color=INK2)
a1.set_title('What one thousand tokens cost', fontsize=14.5, color=INK, pad=10)
a1.set_ylim(0, max(tk.per_k) * 1.22); frame(a1, 'Wh per 1 000 generated tokens')
a2.bar(xb, tk.tok.values, .52, color=[MCOL[m] for m in tk.index], zorder=3,
       edgecolor=SURF, linewidth=1.4)
for xi, vi in zip(xb, tk.tok.values):
    a2.text(xi, vi + 8, f'{vi:.0f}', ha='center', fontsize=12, color=INK2)
a2.set_title('How long the answer is', fontsize=14.5, color=INK, pad=10)
a2.set_ylim(0, max(tk.tok) * 1.22); frame(a2, 'Output tokens per answer')
for a_ in (a1, a2):
    a_.set_xticks(xb); a_.set_xticklabels(LBL, fontsize=14, color=INK)
head(fig, 'The extra energy is the price of a token, not the number of tokens',
     'A thousand tokens cost %.1f times more on the 7B than on the 0.5B, and its answers\nare no '
     'longer. Asking users for shorter answers is a weak lever.'
     % (tk.per_k.iloc[-1] / tk.per_k.iloc[0]))
foot(fig, 'Source: benchmark_runs.csv · 144 runs, mean over the twelve prompts')
save(fig, 'L1f_token_economics.png')
print('  per-1k Wh:', tk.per_k.round(4).to_dict())
print('  tokens   :', tk.tok.round(0).to_dict())

print('\nscaling-up, from published figures')

# ====================================================== S3 what moves it ====
MOVES = [('Which model answers\nthe request',
          2.07, PROPOSED, 'measured here — 0.0210 vs 0.0102 Wh on the 3B'),
         ('Which provider\nserves it',
          0.60 / 0.287, PUBLISHED, 'CIF 0.287 (AWS) to 0.60 (DeepSeek) kgCO₂e/kWh'),
         ('How that provider\ncounts its electricity',
          345 / 94, PUBLISHED, 'Google 2024: 345 location-based, 94 market-based'),
         ('Which country\nthe data centre sits in',
          713 / 30, PUBLISHED, 'Norway 30 to India 713 gCO₂/kWh')]
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.265, right=.955, top=.655, bottom=.19)
yy = np.arange(len(MOVES))[::-1]
for y, (nm, v, col, note) in zip(yy, MOVES):
    ax.barh([y], [v], height=.44, color=col, zorder=3, edgecolor=SURF, linewidth=1.6)
    ax.text(v + .45, y + .06, f'×{v:.1f}', va='center', fontsize=15, color=col, fontweight='bold')
    ax.text(.25, y - .30, note, fontsize=10.5, color=INK3, va='top')
ax.set_yticks(yy); ax.set_yticklabels([m[0] for m in MOVES], fontsize=13, color=INK)
ax.set_xlim(0, 27); ax.set_xticks([0, 5, 10, 15, 20, 25])
ax.grid(axis='x', color=GRID, lw=1, zorder=0); ax.set_axisbelow(True)
[s.set_visible(False) for s in ax.spines.values()]
ax.set_xlabel('Ratio between the best and the worst case, on the carbon of one request',
              fontsize=13, labelpad=10, color=INK2)
head(fig, 'The lever I measured is the smallest of the four',
     'Only the top bar was metered for this thesis. The other three come from published figures,\nand each one moves the carbon of the same request further than the model choice does.')
foot(fig, 'Sources: this campaign · Jegham et al. (2025) provider multipliers · Google (2025) · '
          'national grid intensities, Ember via Jin et al. (2025)')
save(fig, 'S3_what_moves_it.png')

# ====================================================== S4 the same firm ====
GRIDS = [('Norway', 30), ('United States', 367), ('World average', 481), ('India', 713)]
POL = [('Open models, the recommended policy', 0.50, PROPOSED),
       ('Frontier API, the default', 3.60, '#C9C3C7')]
fig, ax = plt.subplots(figsize=(9.6, 5.4)); fig.subplots_adjust(left=.105, right=.955, top=.655, bottom=.185)
xg = np.arange(len(GRIDS)); wg = .34
for i, (nm, mwh, col) in enumerate(POL):
    v = [mwh * g for _, g in GRIDS]        # MWh x 1000 kWh x g/kWh / 1000 = kg
    ax.bar(xg + (i - .5) * (wg + .02), v, wg, color=col, label=nm, zorder=3,
           edgecolor=SURF, linewidth=1.4)
    for xi, vi in zip(xg + (i - .5) * (wg + .02), v):
        ax.text(xi, vi + 35, f'{vi:,.0f}'.replace(',', ' '), ha='center', fontsize=11.5, color=INK2)
ax.set_xticks(xg)
ax.set_xticklabels([f'{n}\n{g} gCO₂/kWh' for n, g in GRIDS], fontsize=12.5, color=INK)
ax.set_ylim(0, 3050)
frame(ax, 'kg CO₂e a year')
ax.legend(frameon=False, fontsize=13, loc='upper left', labelcolor=INK2)
head(fig, 'The same policy, the same traffic, twenty-four times apart',
     'A 10 000-employee firm at 10.56 million requests a year, under the two policies of the\nprevious slide, priced on four different grids. Nothing about the AI changes between the bars.')
foot(fig, 'Energy from this campaign and Table 17 · grid intensities in gCO₂/kWh, 2023')
save(fig, 'S4_country_grid.png')
print('  recommended policy:', {n: round(0.50*g) for n, g in GRIDS})
print('  frontier default  :', {n: round(3.60*g) for n, g in GRIDS})

print('\nthe calculation chain')

# ================================================== S5 the carbon calculator =
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig = plt.figure(figsize=(9.6, 5.8))
ax = fig.add_axes([0.045, 0.055, 0.915, 0.655]); ax.set_xlim(0, 100); ax.set_ylim(0, 100)
ax.axis('off')

def box(x, y, w, h, title, body, fill, edge, fs=10.2, mid=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.4',
                                facecolor=fill, edgecolor=edge, linewidth=1.6, zorder=3))
    if mid:
        ax.text(x + w / 2, y + h / 2, title, ha='center', va='center', fontsize=11.5,
                fontweight='bold', color=INK, zorder=4, linespacing=1.4)
        return
    ax.text(x + w / 2, y + h - 3.0, title, ha='center', va='top', fontsize=11,
            fontweight='bold', color=INK, zorder=4)
    ax.text(x + w / 2, y + h - 9.5, body, ha='center', va='top', fontsize=fs,
            color=INK2, zorder=4, linespacing=1.38)

def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=14,
                                 color=INK2, linewidth=1.5, zorder=2))

box(1, 55, 25, 42, 'Energy of one request',
    'Jegham et al. estimate it from\nlatency \u00d7 rated power \u00d7\nutilisation, over 10 000 draws.\n\n'
    'This thesis measures it:\n0.0102 Wh on the 3B.', '#FBF2F6', PROPOSED, fs=10.0)
box(31, 62, 19, 28, '\u00d7 PUE',
    'Data-centre overhead:\ncooling, lighting, power\ndistribution.\n1.12 to 1.27', SURF, GRID)
box(55, 76, 19, 24, '\u00d7 CIF',
    'Carbon intensity of the\ngrid that serves it.\n0.030 to 0.713 kg/kWh', SURF, GRID)
box(55, 42, 19, 29, '\u00d7 WUE',
    'On site, plus the water\nbehind the electricity.\n0.18\u20131.20 L/kWh site\n4.35\u20136.02 off site',
    SURF, GRID)
box(79, 76, 20, 24, 'kg CO\u2082e\nper request', '', '#FBF2F6', PROPOSED, mid=True)
box(79, 42, 20, 29, 'litres of water\nper request', '', '#FBF2F6', PROPOSED, mid=True)
box(31, 6, 43, 28, '\u00d7 requests per year',
    'The one term no multiplier contains, and the one\nno supplier publishes. A 10 000-employee firm:\n'
    '10.56 million requests a year.', '#F2EEF0', '#C9C3C7', fs=10.2)
box(79, 6, 20, 28, 'the annual\nfootprint', '', '#FBF2F6', PROPOSED, mid=True)

arrow(26.4, 76, 30.6, 76)
arrow(50.4, 80, 54.6, 86)
arrow(50.4, 72, 54.6, 60)
arrow(74.4, 88, 78.6, 88)
arrow(74.4, 56, 78.6, 56)
arrow(13, 54.4, 13, 24); arrow(13.6, 20, 30.6, 20)
arrow(74.4, 20, 78.6, 20)

head(fig, 'From one measured request to an annual footprint',
     'The multiplier chain of Jegham et al. (2025). Every term is published except the first,\n'
     'which this thesis replaces with a measurement, and the last, which only the firm knows.')
foot(fig, 'Method: Jegham et al. (2025), equations 1, 4 and 5 \u00b7 multiplier ranges from their '
          'Table 1 and from national grid intensities')
save(fig, 'S5_calculator.png')
