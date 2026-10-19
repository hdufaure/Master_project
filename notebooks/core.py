"""MOCK core.py for testing: real figure helpers, synthetic measurements."""
import random, time
from pathlib import Path
import pandas as pd

OLLAMA_URL="http://localhost:11434"; SEED=42; CONTEXT_TOKENS=4096; MAX_NEW_TOKENS=1024
OUTPUTS=Path("outputs"); FIGURES=OUTPUTS/"figures"; OUTPUTS.mkdir(exist_ok=True); FIGURES.mkdir(exist_ok=True)
SIZES={"qwen2.5:0.5b":0.5,"qwen2.5:1.5b":1.5,"qwen2.5:3b":3.0,"qwen2.5:7b":7.0,"llama3.1:8b":8.0}
_rng=random.Random(SEED)
ANSWERS=["Canberra.","14/05/2025","2480,50","Technique","Facturation",
 "The meeting is postponed to Tuesday.","The delivery is delayed by one week.",
 "2025-03-07","+33612345678","OK","NON",
 '{"exactitude":4,"clarte":4,"structure":3,"completude":4,"utilite":3,"commentaire":"ok"}',
 '{"date":"12/03/2025","montant":"1250,00","categorie":"logiciel"}',
 '{"categorie":"Technique","urgence":"haute","equipe":"support"}',
 '{"nom":"Jean Dupont","telephone":"+33612345678","email":"jean.dupont@exemple.fr"}']
def unload(model): pass
def ask(model, prompt, max_new_tokens=MAX_NEW_TOKENS, unload_first=True):
    size=SIZES.get(model,1.0); tokens=min(max_new_tokens,_rng.randint(40,300))
    return {"model":model,"answer":_rng.choice(ANSWERS),
            "energy_wh":round(0.02*size**0.66*tokens/100,5),
            "duration_s":round(0.5*size*tokens/100,3),
            "load_s":round(0.9+1.1*size,3) if unload_first else 0.0,
            "tokens_out":tokens,"tokens_in":_rng.randint(20,400)}
def idle_watts(seconds=30,samples=3): return round(_rng.uniform(9.5,10.5),3)
def describe_machine(): return {"os":"mock","cpu":"mock","logical_cores":8,"ram_gb":16.0,"python":"3.11"}
def save_table(frame,name):
    p=OUTPUTS/f"{name}.csv"; frame.to_csv(p,index=False,encoding="utf-8-sig")
    print(f"saved {p}  ({len(frame)} rows)"); return frame

# ------------------------------------------------------------------- figures
# One blue ramp, light to dark, in order of model size: the darker the bar,
# the more parameters. Blue against orange wherever two pipelines are compared,
# because that pair stays distinguishable in greyscale and for colour-blind readers.

MODEL_COLOURS = {"qwen2.5:0.5b": "#9DC1EA", "qwen2.5:1.5b": "#5E9AE0",
                 "qwen2.5:3b": "#2A78D6", "qwen2.5:7b": "#1A4E8A"}
BASELINE_COLOUR = "#1A4E8A"
CASCADE_COLOUR = "#E07B39"
INK = "#1A1A1A"
MUTED = "#5A6472"
GRID = "#E4E4E1"

TIER_LABELS = {"T1": "Routine (T1)", "T2": "Analytical (T2)", "T3": "Complex (T3)"}


def model_label(model):
    """qwen2.5:1.5b -> 1.5B"""
    return model.split(":")[-1].upper()


def new_figure(title, subtitle, ylabel, width=11, height=6.2):
    """A figure with the title, subtitle and axes used throughout. Returns (figure, axes)."""
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Calibri", "Carlito", "DejaVu Sans"]})
    figure, axes = plt.subplots(figsize=(width, height))
    axes.set_title(title, fontsize=14, weight="bold", loc="left", color=INK, pad=74)
    axes.text(0, 1.105, subtitle, transform=axes.transAxes, fontsize=9.5, color=MUTED)
    axes.set_ylabel(ylabel, fontsize=10, color=MUTED)
    axes.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    axes.set_axisbelow(True)
    axes.tick_params(colors=MUTED, length=0, labelsize=9.5)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color(GRID)
    return figure, axes


def save_figure(figure, axes, name, legend_columns=4):
    """Place the legend above the plot, write the PNG, close the figure."""
    import matplotlib.pyplot as plt

    if axes.get_legend_handles_labels()[0]:
        axes.legend(frameon=False, ncol=legend_columns, loc="lower left",
                    bbox_to_anchor=(0, 1.005), fontsize=10, labelcolor=MUTED)
    figure.tight_layout()
    path = FIGURES / f"{name}.png"
    figure.savefig(path, dpi=190, bbox_inches="tight")
    plt.close(figure)
    print(f"saved {path}")
