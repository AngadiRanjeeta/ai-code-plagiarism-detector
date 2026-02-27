from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
from ast_features import get_normalized_ast
from similarity import compute_similarity, structural_similarity
import difflib

app = Flask(__name__)

# Load transformer model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    code1 = request.form["code1"]
    code2 = request.form["code2"]

    # ---------------------------
    # Semantic Similarity
    # ---------------------------
    emb1 = model.encode(code1)
    emb2 = model.encode(code2)
    semantic_score = compute_similarity(emb1, emb2)

    # ---------------------------
    # Structural Similarity (AST)
    # ---------------------------
    ast1 = get_normalized_ast(code1)
    ast2 = get_normalized_ast(code2)
    struct_score = structural_similarity(ast1, ast2)

    # ---------------------------
    # Hybrid Final Score
    # ---------------------------
    final_score = 0.7 * semantic_score + 0.3 * struct_score

    # ---------------------------
    # Verdict + Confidence
    # ---------------------------
    if final_score > 0.85:
        verdict = "⚠ Highly Likely Plagiarized"
        confidence = "High Confidence"
    elif final_score > 0.65:
        verdict = "⚠ Moderate Similarity"
        confidence = "Medium Confidence"
    else:
        verdict = "✓ Likely Different"
        confidence = "Low Similarity"

    # ---------------------------
    # Code Diff Highlighting
    # ---------------------------
    diff = difflib.ndiff(code1.splitlines(), code2.splitlines())

    diff_html = ""
    for line in diff:
        if line.startswith("+ "):
            diff_html += f"<div class='diff-added'>{line}</div>"
        elif line.startswith("- "):
            diff_html += f"<div class='diff-removed'>{line}</div>"
        else:
            diff_html += f"<div>{line}</div>"

    return render_template(
        "index.html",
        semantic=round(semantic_score, 3),
        structural=round(struct_score, 3),
        final=round(final_score, 3),
        verdict=verdict,
        confidence=confidence,
        diff_output=diff_html,
    )


if __name__ == "__main__":
    app.run(debug=True)