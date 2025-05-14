import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

rekvizitai = pd.read_csv("rekvizitai/rekvizitai.csv", sep=';')  
processed_mega_dataset = pd.read_csv("processed_mega_dataset.csv")  

# Preprocess
rekvizitai['Company'] = rekvizitai['Company'].str.strip()  # Strip whitespace
processed_mega_dataset['Company'] = processed_mega_dataset['Company'].str.strip()

# Remove dots apostrophes and other special characters
rekvizitai['CCompany'] = rekvizitai['Company'].str.replace(r'[^\w\s]', '', regex=True)
processed_mega_dataset['CCompany'] = processed_mega_dataset['Company'].str.replace(r'[^\w\s]', '', regex=True)
# Lowercase everything 
rekvizitai['CCompany'] = rekvizitai['CCompany'].str.lower()
processed_mega_dataset['CCompany'] = processed_mega_dataset['CCompany'].str.lower()

rekvizitai['First Word'] = rekvizitai['CCompany'].str.split().str[0]
processed_mega_dataset['First Word'] = processed_mega_dataset['CCompany'].str.split().str[0]


for first_word in rekvizitai['First Word']:
    # Filter postings by company and count them
    matching_jobs = processed_mega_dataset[processed_mega_dataset['First Word'] == first_word]
    total_hiring = len(matching_jobs)
    rekvizitai.loc[rekvizitai['First Word'] == first_word, 'Total Hiring'] = total_hiring

rekvizitai = rekvizitai.drop(columns=['First Word'])
rekvizitai.to_csv("rekvizitai/rekvizitai_updated.csv", sep=';', index=False)

# Sort
rekvizitai['Projected'] = rekvizitai['Employees'] + rekvizitai['Total Hiring']
rekvizitai = rekvizitai.sort_values('Projected', ascending=False)

# Plot
fig = plt.figure(figsize=(7, 8))
ax = fig.add_subplot(111)
x = range(len(rekvizitai))

counts = rekvizitai['Employees'].tolist() + rekvizitai['Total Hiring'].tolist()
height = max(counts) * 1.2
width = len(rekvizitai)
background = FancyBboxPatch(
    (-0.5, 0), width, height,
    boxstyle=f"round,pad=0,rounding_size={0.05*width}",
    facecolor='#f0f6ff', alpha=0.5, edgecolor='none', zorder=0
)
ax.add_patch(background)

bar1 = ax.bar(x, rekvizitai['Employees'], label='Current Employees', color='#2D7FF9')
bar2 = ax.bar(x, rekvizitai['Total Hiring'], bottom=rekvizitai['Employees'], label='Hiring', color='#A0C577')

# Add labels
ax.set_xticks(x)
ax.set_xticklabels(rekvizitai['Company'], rotation=45, ha='right', fontsize=12)
ax.legend(loc='upper center', fontsize=10 ,fancybox=True, shadow=True, borderpad=1)

for i, total in enumerate(rekvizitai['Total Hiring']):
    total = int(total)
    ax.text(i, total + rekvizitai['Employees'].iloc[i] + 20, f"+{total}", ha='center', va='bottom', fontsize=14, color='black')

plt.tight_layout()
plt.show()

#fig.savefig('newsletter_images/rekvizitai_plot.png', bbox_inches='tight', dpi=300)