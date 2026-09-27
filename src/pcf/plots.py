import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def hotspots(pcf, variants, path):
    cat = pcf.groupby("category")[list(variants.index)].sum()
    cat = cat.loc[cat.sum(axis=1).sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bottom = np.zeros(len(variants))
    colors = plt.cm.tab10.colors
    for i, (name, row) in enumerate(cat.iterrows()):
        ax.bar([f"Pack {v}" for v in variants.index], row.values, bottom=bottom, label=name, color=colors[i % 10])
        bottom += row.values
    ax.set_ylabel("kg CO2e per pack")
    ax.set_title("Cradle-to-gate PCF by category")
    ax.legend(frameon=False, fontsize=8, bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def scenarios(df, path):
    piv = df.pivot(index="scenario", columns="variant", values="reduction_pct")
    fig, ax = plt.subplots(figsize=(7, 3.8))
    y = np.arange(len(piv))
    h = 0.25
    for i, v in enumerate(piv.columns):
        ax.barh(y + (i - 1) * h, piv[v], h, label=f"Pack {v}")
    ax.set_yticks(y, piv.index)
    ax.set_xlabel("PCF reduction vs baseline (%)")
    ax.set_title("Reduction scenarios")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
