# -*- coding: utf-8 -*-
"""Comparecimento (turnout) as % of registered voters, all six elections
(2004-2024), from TSE's detalhe_votacao_{year} extracts (DS_CARGO=Prefeito).

Produces:
  - output/comparecimento_historico.csv
  - output/chart_comparecimento_historico.b64
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os, base64
from io import BytesIO

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "output", "en")
os.makedirs(OUT, exist_ok=True)

_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
for _f in ["Anton-Regular.ttf", "BricolageGrotesque-Regular.ttf", "BricolageGrotesque-SemiBold.ttf", "BricolageGrotesque-Bold.ttf"]:
    _p = os.path.join(_FONT_DIR, _f)
    if os.path.exists(_p):
        fm.fontManager.addfont(_p)
plt.rcParams["font.family"] = "Bricolage Grotesque"

BG = "#ffffff"
INK = "#333333"
MUTED = "#8f8f8f"
GRID = "#e2e2e2"
BLUE = "#2f6690"  # neutral/informational, matches the site's 3-color palette

YEARS = [2004, 2008, 2012, 2016, 2020, 2024]
rows = []
for year in YEARS:
    df = pd.read_csv(os.path.join(DATA, f"detalhe_votacao_{year}_alfredo_chaves.csv"), sep=";", encoding="utf-8")
    df.columns = [c.strip().upper() for c in df.columns]
    row = df[df["DS_CARGO"].str.strip().str.upper() == "PREFEITO"].iloc[0]
    aptos = int(row["QT_APTOS"])
    comparecimento = int(row["QT_COMPARECIMENTO"])
    pct = round(comparecimento / aptos * 100, 2)
    rows.append({"ano": year, "aptos": aptos, "comparecimento": comparecimento, "pct_comparecimento": pct})

df_out = pd.DataFrame(rows)
df_out.to_csv(os.path.join(OUT, "comparecimento_historico.csv"), index=False)
print(df_out.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 5), dpi=160)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(df_out["ano"], df_out["pct_comparecimento"], color=BLUE, linewidth=3, marker="o", markersize=9, zorder=3)
for x, y in zip(df_out["ano"], df_out["pct_comparecimento"]):
    ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 14),
                ha="center", fontsize=12, fontweight="bold", fontfamily="Anton", color=INK)

ax.set_xticks(YEARS)
ax.set_ylim(70, 98)
ax.set_yticks([70, 75, 80, 85, 90, 95])
ax.set_yticklabels([f"{v}%" for v in [70, 75, 80, 85, 90, 95]])
ax.tick_params(colors=MUTED, labelsize=10.5)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color(GRID)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)

fig.text(0.08, 0.97, "TURNOUT DOWN, EVEN AS THE ELECTORATE GREW", fontsize=15, color=INK, fontfamily="Anton", ha="left", va="top")
fig.text(0.08, 0.905, "% of registered voters who cast a ballot, mayoral election, 2004–2024", fontsize=10, color=MUTED, ha="left", va="top")
plt.tight_layout(rect=[0, 0, 1, 0.86])
buf = BytesIO()
plt.savefig(buf, format="png", facecolor=BG)
plt.close(fig)
b64 = base64.b64encode(buf.getvalue()).decode("ascii")
with open(os.path.join(OUT, "chart_comparecimento_historico.b64"), "w", encoding="utf-8") as f:
    f.write(b64)
print("Saved: chart_comparecimento_historico.b64")
