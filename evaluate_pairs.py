# evaluate_pairs.py
import argparse
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

from sentence_transformers import SentenceTransformer

# --- Project imports (must match your repo) ---
from similarity import compute_similarity, structural_similarity
from ast_features import get_normalized_ast
try:
    from preprocess import normalize_code
except Exception:
    # If preprocess.py or normalize_code doesn't exist, fall back to identity
    def normalize_code(x: str) -> str:
        return x


# -------------------------
# Core scoring
# -------------------------
def compute_scores(code1: str, code2: str, model: SentenceTransformer):
    """
    Returns (semantic_score, structural_score, hybrid_score)
    All scores are floats in [0,1] (depending on your similarity functions).
    """
    c1 = normalize_code(str(code1))
    c2 = normalize_code(str(code2))

    # Semantic (SBERT cosine)
    emb1 = model.encode(c1)
    emb2 = model.encode(c2)
    sem = float(compute_similarity(emb1, emb2))

    # Structural (AST Jaccard)
    ast1 = get_normalized_ast(c1)
    ast2 = get_normalized_ast(c2)
    struct = float(structural_similarity(ast1, ast2))

    # Hybrid (70/30)
    hybrid = 0.7 * sem + 0.3 * struct

    # Clamp just in case
    sem = float(np.clip(sem, 0.0, 1.0))
    struct = float(np.clip(struct, 0.0, 1.0))
    hybrid = float(np.clip(hybrid, 0.0, 1.0))

    return sem, struct, hybrid


# -------------------------
# Threshold tuning
# -------------------------
def best_threshold_by_f1(y_true, y_score):
    thresholds = np.linspace(0.0, 1.0, 401)
    best_thr = 0.5
    best_f1 = -1.0

    for t in thresholds:
        y_pred = (y_score >= t).astype(int)
        _, _, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        if f1 > best_f1:
            best_f1 = float(f1)
            best_thr = float(t)

    return best_thr, best_f1


# -------------------------
# Metrics
# -------------------------
def eval_one(y_true, y_score, name: str):
    thr, best_f1 = best_threshold_by_f1(y_true, y_score)
    y_pred = (y_score >= thr).astype(int)

    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )

    # AUC metrics need both classes present
    if len(np.unique(y_true)) > 1:
        auc = roc_auc_score(y_true, y_score)
        pr_auc = average_precision_score(y_true, y_score)
    else:
        auc = float("nan")
        pr_auc = float("nan")

    cm = confusion_matrix(y_true, y_pred)

    return {
        "model": name,
        "best_threshold": float(thr),
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": float(auc),
        "pr_auc": float(pr_auc),
        "confusion_matrix": cm,
        "best_f1_search": float(best_f1),
    }


def bootstrap_auc_ci(y_true, y_score, n=800, seed=42):
    """
    Bootstrap CI for ROC-AUC.
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    if len(np.unique(y_true)) < 2:
        return (float("nan"), float("nan"), float("nan"))

    rng = np.random.default_rng(seed)
    idx = np.arange(len(y_true))
    aucs = []

    for _ in range(n):
        sample = rng.choice(idx, size=len(idx), replace=True)
        yt = y_true[sample]
        ys = y_score[sample]
        if len(np.unique(yt)) < 2:
            continue
        aucs.append(roc_auc_score(yt, ys))

    if not aucs:
        return (float("nan"), float("nan"), float("nan"))

    aucs = np.array(aucs)
    mean = float(np.mean(aucs))
    lo = float(np.quantile(aucs, 0.025))
    hi = float(np.quantile(aucs, 0.975))
    return mean, lo, hi


# -------------------------
# Markdown output
# -------------------------
def save_results_markdown(results, dataset_path: str, out_path: str = "evaluation_results.md"):
    """
    Creates a README-ready markdown file with a nice table.
    """
    # Find hybrid result (fallback to first result if not found)
    hybrid = None
    for r in results:
        if "Hybrid" in r["model"]:
            hybrid = r
            break
    if hybrid is None:
        hybrid = results[0]

    # Also create a model comparison table
    rows_md = []
    for r in results:
        rows_md.append(
            f"| {r['model']} | {r['accuracy']:.2f} | {r['precision']:.2f} | {r['recall']:.2f} | {r['f1']:.3f} | {r['roc_auc']:.3f} |"
        )

    md = f"""# Evaluation Results

Dataset: `{dataset_path}`

## Summary (Best / Hybrid)

| Metric | Value |
|---|---:|
| Accuracy | **{hybrid['accuracy']*100:.0f}%** |
| Precision | **{hybrid['precision']*100:.0f}%** |
| Recall | **{hybrid['recall']*100:.0f}%** |
| F1 Score | **{hybrid['f1']:.3f}** |
| ROC-AUC | **{hybrid['roc_auc']:.3f}** |
| PR-AUC | **{hybrid['pr_auc']:.3f}** |
| Best Threshold (F1) | **{hybrid['best_threshold']:.3f}** |

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows_md)}

> Confusion matrix format: `[[TN, FP], [FN, TP]]`
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n📄 {out_path} created successfully!")


# -------------------------
# Main
# -------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/pairs.csv", help="CSV with columns: code1, code2, label")
    ap.add_argument("--limit", type=int, default=None, help="Optional: limit rows for quick tests")
    ap.add_argument("--bootstrap", action="store_true", help="Add bootstrap CI for Hybrid ROC-AUC")
    ap.add_argument("--out_md", default="evaluation_results.md", help="Markdown output file name")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    required = {"code1", "code2", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}. Required: {sorted(required)}")

    if args.limit:
        df = df.head(args.limit)

    y_true = df["label"].astype(int).to_numpy()

    # Load SBERT model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    sem_scores = []
    struct_scores = []
    hybrid_scores = []

    for c1, c2 in zip(df["code1"].astype(str), df["code2"].astype(str)):
        sem, struct, hybrid = compute_scores(c1, c2, model)
        sem_scores.append(sem)
        struct_scores.append(struct)
        hybrid_scores.append(hybrid)

    sem_scores = np.array(sem_scores, dtype=float)
    struct_scores = np.array(struct_scores, dtype=float)
    hybrid_scores = np.array(hybrid_scores, dtype=float)

    results = [
        eval_one(y_true, sem_scores, "Semantic-only (SBERT cosine)"),
        eval_one(y_true, struct_scores, "Structural-only (AST Jaccard)"),
        eval_one(y_true, hybrid_scores, "Hybrid (0.7 semantic + 0.3 structural)"),
    ]

    # Print summary
    print("\n=== Evaluation Summary ===")
    for r in results:
        cm = r["confusion_matrix"]
        print(f"\n[{r['model']}]")
        print(f"  Best threshold (F1): {r['best_threshold']:.3f}")
        print(f"  Accuracy:  {r['accuracy']:.4f}")
        print(f"  Precision: {r['precision']:.4f}")
        print(f"  Recall:    {r['recall']:.4f}")
        print(f"  F1:        {r['f1']:.4f}")
        print(f"  ROC-AUC:   {r['roc_auc']:.4f}")
        print(f"  PR-AUC:    {r['pr_auc']:.4f}")
        print(f"  Confusion Matrix [[TN FP],[FN TP]]:\n{cm}")

    # Impact numbers
    by_name = {r["model"]: r for r in results}
    hybrid = by_name["Hybrid (0.7 semantic + 0.3 structural)"]
    sem = by_name["Semantic-only (SBERT cosine)"]
    struct = by_name["Structural-only (AST Jaccard)"]

    def delta(a, b):
        a = a if np.isfinite(a) else np.nan
        b = b if np.isfinite(b) else np.nan
        return a - b

    print("\n=== Impact (Hybrid improvement) ===")
    print(f"ΔF1 vs Semantic-only:   {delta(hybrid['f1'], sem['f1']):+.4f}")
    print(f"ΔF1 vs Structural-only: {delta(hybrid['f1'], struct['f1']):+.4f}")
    print(f"ΔROC-AUC vs Semantic-only:   {delta(hybrid['roc_auc'], sem['roc_auc']):+.4f}")
    print(f"ΔROC-AUC vs Structural-only: {delta(hybrid['roc_auc'], struct['roc_auc']):+.4f}")

    if args.bootstrap:
        mean_auc, lo, hi = bootstrap_auc_ci(y_true, hybrid_scores, n=800)
        print("\n=== Hybrid ROC-AUC Bootstrap CI ===")
        print(f"ROC-AUC mean: {mean_auc:.4f} | 95% CI: [{lo:.4f}, {hi:.4f}]")

    # Save per-row scores
    out = df.copy()
    out["semantic_score"] = sem_scores
    out["structural_score"] = struct_scores
    out["hybrid_score"] = hybrid_scores
    out.to_csv("evaluation_outputs.csv", index=False)
    print("\nSaved: evaluation_outputs.csv")

    # Create markdown report automatically
    save_results_markdown(results, dataset_path=args.csv, out_path=args.out_md)


if __name__ == "__main__":
    main()