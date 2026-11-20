
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
results = ROOT / "results" / "preview"

with open(results / "summary.json", encoding="utf-8") as f:
    data = json.load(f)

scores = data["methods"]["tfidf_logistic"]["per_seed"]

seeds = ["42", "123", "2026"]
accuracy = [scores[s]["accuracy"] * 100 for s in seeds]
f1 = [scores[s]["anomaly_f1"] * 100 for s in seeds]

x = range(len(seeds))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))

bars1 = ax.bar(
    [i - width / 2 for i in x],
    accuracy, width, label="Accuracy"
)
bars2 = ax.bar(
    [i + width / 2 for i in x],
    f1, width, label="F1-score Anomaly"
)

ax.set_title("Baseline HDFS - Resultats Preview")
ax.set_xlabel("Graine aleatoire")
ax.set_ylabel("Performance (%)")
ax.set_xticks(list(x))
ax.set_xticklabels(seeds)
ax.set_ylim(0, 105)
ax.legend()
ax.grid(axis="y", alpha=0.25)

ax.bar_label(bars1, fmt="%.2f%%", padding=3)
ax.bar_label(bars2, fmt="%.2f%%", padding=3)

plt.tight_layout()

output = results / "baseline_performance.png"
plt.savefig(output, dpi=300)
plt.close()

print("Graphique cree :", output)
