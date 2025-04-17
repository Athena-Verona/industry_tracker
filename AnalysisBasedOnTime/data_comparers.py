import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==== CONFIGURATION ====
file_earlier = "processed_cvbankas_data.csv"
file_later = "processed_cvbankas_data (2025-04-17).csv"
plot_dir = "job_category_analysis_plots"
os.makedirs(plot_dir, exist_ok=True)

# ==== LOAD DATA ====
df_earlier = pd.read_csv(file_earlier)
df_later = pd.read_csv(file_later)

# ==== AGGREGATE & COMPARE ====
grouped_earlier = df_earlier.groupby("job_category").agg(
    count_earlier=("avg_salary", "count"),
    avg_salary_earlier=("avg_salary", "mean")
).reset_index()

grouped_later = df_later.groupby("job_category").agg(
    count_later=("avg_salary", "count"),
    avg_salary_later=("avg_salary", "mean")
).reset_index()

comparison = pd.merge(grouped_earlier, grouped_later, on="job_category", how="outer").fillna(0)
comparison["count_change"] = comparison["count_later"] - comparison["count_earlier"]
comparison["avg_salary_change"] = comparison["avg_salary_later"] - comparison["avg_salary_earlier"]
comparison["avg_salary_pct_change"] = (
    (comparison["avg_salary_later"] - comparison["avg_salary_earlier"]) /
    comparison["avg_salary_earlier"].replace(0, 1) * 100
)

# ==== PLOTTING SETTINGS ====
sns.set(style="whitegrid")

# ==== SALARY % CHANGE (ALL CATEGORIES) ====
salary_sorted = comparison.sort_values(by="avg_salary_pct_change", ascending=False)

plt.figure(figsize=(12, 10))
sns.barplot(
    x="avg_salary_pct_change",
    y="job_category",
    data=salary_sorted,
    palette="coolwarm"
)
plt.title("Salary % Change by Job Category")
plt.xlabel("Salary % Change")
plt.ylabel("Job Category")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "salary_pct_change_all_categories.png"))
plt.close()

# ==== POSTING COUNT CHANGE (ALL CATEGORIES) ====
count_sorted = comparison.sort_values(by="count_change", ascending=False)

plt.figure(figsize=(12, 10))
sns.barplot(
    x="count_change",
    y="job_category",
    data=count_sorted,
    palette="Spectral"
)
plt.title("Job Posting Count Change by Job Category")
plt.xlabel("Change in Number of Listings")
plt.ylabel("Job Category")
plt.tight_layout()
plt.savefig(os.path.join(plot_dir, "count_change_all_categories.png"))
plt.close()

# ==== EXPORT SUMMARY TABLE ====
comparison.to_csv(os.path.join(plot_dir, "job_category_comparison_summary.csv"), index=False)

print("Analysis complete. Full-category graphs and summary saved in:", plot_dir)
