import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==== CONFIGURATION ====
file_earlier = "processed_cvbankas_data.csv"
file_later = "processed_cvbankas_data (2025-04-17).csv"

plot_dir_agg = "job_category_analysis_aggregated"
plot_dir_detailed = "job_category_analysis_by_seniority"
os.makedirs(plot_dir_agg, exist_ok=True)
os.makedirs(plot_dir_detailed, exist_ok=True)

# ==== LOAD DATA ====
df_earlier = pd.read_csv(file_earlier)
df_later = pd.read_csv(file_later)

# ========================
# === AGGREGATED VIEW ====
# ========================
grouped_earlier = df_earlier.groupby("job_category").agg(
    count_earlier=("avg_salary", "count"),
    avg_salary_earlier=("avg_salary", "mean")
).reset_index()

grouped_later = df_later.groupby("job_category").agg(
    count_later=("avg_salary", "count"),
    avg_salary_later=("avg_salary", "mean")
).reset_index()

agg_comparison = pd.merge(grouped_earlier, grouped_later, on="job_category", how="outer").fillna(0)
agg_comparison["count_change"] = agg_comparison["count_later"] - agg_comparison["count_earlier"]
agg_comparison["avg_salary_pct_change"] = (
    (agg_comparison["avg_salary_later"] - agg_comparison["avg_salary_earlier"]) /
    agg_comparison["avg_salary_earlier"].replace(0, 1) * 100
)

agg_comparison.to_csv(os.path.join(plot_dir_agg, "summary_aggregated.csv"), index=False)

# --- Plotting Helper ---
def plot_top5(data, value_col, label_col, title_prefix, filename_prefix, folder):
    top_positive = data.sort_values(by=value_col, ascending=False).head(5)
    top_negative = data.sort_values(by=value_col, ascending=True).head(5)

    def plot_single(df, color, title, file_suffix):
        plt.figure(figsize=(10, 6))
        bars = sns.barplot(
            x=label_col, y=value_col, data=df, hue=label_col, palette=[color] * len(df), legend=False
        )
        plt.title(title)
        plt.ylabel(value_col.replace("_", " ").title())
        plt.xlabel("")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        for bar in bars.containers[0]:
            height = bar.get_height()
            bars.annotate(
                f"{height:+.1f}",
                (bar.get_x() + bar.get_width() / 2, height),
                ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=10, fontweight='bold'
            )

        plt.savefig(os.path.join(folder, f"{filename_prefix}_{file_suffix}.png"))
        plt.close()

    plot_single(top_positive, "#4CAF50", f"Top 5 ↑ {title_prefix}", "top5_positive")
    plot_single(top_negative, "#F44336", f"Top 5 ↓ {title_prefix}", "top5_negative")



# --- Aggregated Plots ---
plot_top5(
    agg_comparison[(agg_comparison["avg_salary_pct_change"] != 0)],
    "avg_salary_pct_change", "job_category",
    "Salary % Change by Job Category", "salary_pct_change", plot_dir_agg
)

plot_top5(
    agg_comparison[(agg_comparison["count_change"] != 0)],
    "count_change", "job_category",
    "Job Posting Count Change by Job Category", "count_change", plot_dir_agg,
)

# =========================
# === DETAILED VIEW =======
# =========================
grouped_earlier_d = df_earlier.groupby(["job_category", "seniority"]).agg(
    count_earlier=("avg_salary", "count"),
    avg_salary_earlier=("avg_salary", "mean")
).reset_index()

grouped_later_d = df_later.groupby(["job_category", "seniority"]).agg(
    count_later=("avg_salary", "count"),
    avg_salary_later=("avg_salary", "mean")
).reset_index()

detailed_comparison = pd.merge(grouped_earlier_d, grouped_later_d,
                               on=["job_category", "seniority"], how="outer").fillna(0)

detailed_comparison["count_change"] = detailed_comparison["count_later"] - detailed_comparison["count_earlier"]
detailed_comparison["avg_salary_pct_change"] = (
    (detailed_comparison["avg_salary_later"] - detailed_comparison["avg_salary_earlier"]) /
    detailed_comparison["avg_salary_earlier"].replace(0, 1) * 100
)

detailed_comparison["label"] = detailed_comparison["job_category"] + " (" + detailed_comparison["seniority"] + ")"
detailed_comparison.to_csv(os.path.join(plot_dir_detailed, "summary_by_seniority.csv"), index=False)

# --- Detailed Plots ---
plot_top5(
    detailed_comparison[(detailed_comparison["avg_salary_pct_change"] != 0)],
    "avg_salary_pct_change", "label",
    "Salary % Change by Job and Seniority", "salary_pct_change", plot_dir_detailed
)

plot_top5(
    detailed_comparison[(detailed_comparison["count_change"] != 0)],
    "count_change", "label",
    "Job Posting Count Change by Job and Seniority", "count_change", plot_dir_detailed,
)

print("✅ All top 5 increase/decrease plots and summaries saved.")
