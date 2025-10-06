import pandas as pd

# Load your batch summary
df = pd.read_csv("outputs/batch_matrix.csv")

# --- Ranking Logic ---

def rank_best_per_jd(df, score_col="overall_score", top_n=3):
    ranked = []
    for jd in df["jd_filename"].unique():
        jd_sub = df[df["jd_filename"] == jd]
        sorted_sub = jd_sub.sort_values(score_col, ascending=False).head(top_n)
        ranked.append(sorted_sub)
    return pd.concat(ranked)

# Run the ranking
top_n = 3
score_col = "overall_score"  # (You could prompt user for ATS or overall)
finalists = rank_best_per_jd(df, score_col=score_col, top_n=top_n)

print("--- Top Candidates per JD ---\n")
for jd in df["jd_filename"].unique():
    print(f"== {jd} ==")
    best = finalists[finalists["jd_filename"] == jd]
    print(best[["resume_filename", score_col, "ats_composite_score", "report_path"]])
    print()

# Save as a new CSV and/or Excel for easy sharing
finalists.to_csv("outputs/top_candidates_per_jd.csv", index=False)
print("Best-fit list saved as outputs/top_candidates_per_jd.csv")
