import pandas as pd
from collections import Counter

df1 = pd.read_csv('cvbankas_jobs_with_skills.csv', sep=';')
df2 = pd.read_csv('cvonline_jobs_with_skills.csv', sep=';')

skills_series = pd.concat([df1['Skills'], df2['Skills']], ignore_index=True)

all_skills = []

for entry in skills_series.dropna():
    skills = [s.strip().lower() for s in str(entry).split(',')]
    all_skills.extend(skills)

skill_counts = Counter(all_skills)

top_n = 20
print(f"\nTop {top_n} most popular skills:")
for skill, count in skill_counts.most_common(top_n):
    print(f"{skill}: {count}")
