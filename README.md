# Measuring the inference energy of small language models

Code, data and figures behind a Master Project at EDHEC Business School on
reducing the environmental cost of generative AI in organizations.

Four measurement campaigns on one machine, every request metered, asking a
narrow question: **can the energy of inference be cut without losing quality or
latency, and does the saving come from choosing the model or from routing
between models at run time?**

The short answer is that it comes from the choice, made once, before any request
arrives — and that the run-time mechanism costs more than it saves.

## What was measured

| Campaign | Design | Runs |
|---|---|---|
| Benchmark | 4 Qwen2.5 models (0.5B, 1.5B, 3B, 7B) × 12 prompts × 3 repetitions, graded by two independent judges | 144 |
| Cascade | always-7B against a 0.5B → 3B → 7B cascade with a 1.5B verifier, executed end to end | 24 |
| Prompt specialisation | 8 narrow tasks × 5 configurations (model size × prompt style) | 40 |
| Model specialisation | 20 programming tasks × 7 configurations, every answer graded by executing it | 140 |

All four models run under Q4_K_M quantisation through Ollama, on a laptop with
an Intel Core i7-1260P and no GPU. Energy is whole-machine energy sampled once a
second by CodeCarbon 3.2.6.

## What came out of it

- Energy per request rises with model size, and the cost is in the price of a
  token rather than in the length of the answer: from the 0.5B to the 7B, the
  energy of a thousand generated tokens rises by a factor of 6.1 while answers
  get slightly *shorter*.
- Judged quality rises with size up to three billion parameters and then stops.
  The 7B costs 80.6 % more energy than the 3B for a quality difference the
  measurements cannot separate from zero.
- Choosing the 3B once, for a stated 60/30/10 workload, uses **51.6 % less
  energy** than always calling the 7B, answers 2.4 times faster, and raises
  acceptable answers from 82.5 % to 91.2 %.
- Executed end to end, the cascade cuts energy by 69.7 % — and correct answers
  from 6 of 7 to 4 of 7. The verifier accepted the small model's answer on ten of
  twelve requests, three of them wrongly. **The accuracy loss is the verifier's
  false-accept rate, not a property of cascading.** Verification alone costs 34 %
  of the pipeline's energy.
- An output contract lets a 1.5B match a 7B for 67 % less energy; a code-trained
  3B matches a general 7B for 50.5 % less. At equal parameter count,
  specialisation changes nothing — it lowers the size at which a task becomes
  feasible, and the saving is the smaller model's.

## Layout

```
notebooks/   the five notebooks, in the order they were run
data/        every CSV they wrote, plus the runs that were set aside
figures/     the 17 figures, and the script that regenerates them
sources.md   each citation mapped to the exact place it comes from
```

| Notebook | What it does |
|---|---|
| [`01_benchmark.ipynb`](notebooks/01_benchmark.ipynb) | the benchmark campaign and its statistics |
| [`02_cascade.ipynb`](notebooks/02_cascade.ipynb) | the two pipelines, executed end to end |
| [`03_specialisation.ipynb`](notebooks/03_specialisation.ipynb) | prompt specialisation on eight narrow tasks |
| [`04_coder_vs_general.ipynb`](notebooks/04_coder_vs_general.ipynb) | a code-trained model against its general twin |
| [`05_scaling_cloud.ipynb`](notebooks/05_scaling_cloud.ipynb) | no new measurement: published multipliers applied to the CSVs above |

## Checking the numbers

Every headline figure in the write-up is recomputed from the raw CSVs by one
script:

```bash
pip install pandas numpy && python verify.py
```

It prints each claim beside the value it recomputes and exits non-zero if any of
them disagree. Nothing is hard-coded except the claimed figure itself.

```
always-3B against always-7B, energy saved (%)       51.6 %     51.59 %  ok
cascade against always-7B, energy saved (%)         69.7 %     69.69 %  ok
verifier false accepts                             3 of 10     3 of 10  ok
...
19 of 19 checks reproduce the published figure.
```

## Running it without installing anything

Two notebooks need nothing but pandas and matplotlib, so they open straight in
Colab:

- [`05_scaling_cloud.ipynb`](https://colab.research.google.com/github/hdufaure/ai-inference-energy/blob/main/notebooks/05_scaling_cloud.ipynb) — the cloud extrapolation
- the figure script runs the same way: `!git clone` the repo, then `cd ai-inference-energy/figures && python gen.py`

The four measurement notebooks cannot run in Colab — they need a local Ollama
server and a power meter on the host.

## Reproducing

Figures, from the data already here:

```bash
cd figures && pip install pandas numpy matplotlib && python gen.py
```

Measurements, from scratch: a local Ollama server with `qwen2.5` at 0.5b, 1.5b,
3b and 7b, `qwen2.5-coder`, and `llama3.1:8b`, then
`pip install -r notebooks/requirements.txt`. Temperature is 0 and the seed is
fixed, so re-running returns the same answers — but not the same watt-hours,
which depend on the machine.

## Runs that were set aside

`data/discarded_runs/` holds two sets of measurements that are reported nowhere,
kept here because discarding data silently would defeat the point of publishing
it.

- `specialisation_runs_fixed_order.csv` — an earlier run in which the five
  configurations were always presented in the same order, so a configuration
  could benefit from a model the previous one had just loaded. The campaign was
  re-run with randomised order, and that re-run is the one reported.
- `blockB_runs_flawed_protocol.csv` — a campaign that only ever ran under that
  same flawed protocol, and was therefore never usable.

## Caveats worth reading before reusing any of this

Energy comes from CodeCarbon's power model on a CPU-only machine, not from a
hardware sensor. Absolute watt-hours are not transferable; the ratios between
configurations measured on the same instrument are what the work rests on.
Twelve prompts support paired comparisons on energy but leave quality
comparisons underpowered, and the cascade's accuracy gap rests on seven
verifiable prompts.

One model family, one quantisation, one machine, and all four sizes fall in the
smallest of the published GPU classes. Nothing here establishes what happens
above seven billion parameters.

## Not in this repository

The thesis itself and the practitioner interview are not published here. The
written document is available on request.

## Author

Hugo Dufaure de Lajarte — EDHEC Business School & Centrale Lille
