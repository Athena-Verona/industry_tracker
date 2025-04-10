import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from collections import Counter

# Set the visual style for plots
plt.style.use('ggplot')
sns.set_palette("viridis")

def main():
    print("Loading and analyzing job salary data...")
    
    try:
        df = pd.read_csv('cvonline_jobs.csv', delimiter=';')
        print(f"Successfully loaded data with {len(df)} job listings")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    df = clean_data(df)
    df = categorize_jobs(df)
    analyze_salaries(df)
    create_visualizations(df)
    
    df.to_csv('processed_salary_data.csv', index=False)
    print("Analysis complete!")

def clean_data(df):
    print("Cleaning and preparing data...")
    
    df = df.copy()
    
    df['min_salary'], df['max_salary'] = zip(*df['Salary'].apply(extract_salary_range)) #PROBLEM 1!
    df['avg_salary'] = (df['min_salary'] + df['max_salary']) / 2
    df['salary_range'] = df['max_salary'] - df['min_salary']
    
    # Remove rows with no salary info
    original_count = len(df)
    df = df.dropna(subset=['min_salary', 'max_salary'])
    print(f"Removed {original_count - len(df)} rows with missing salary information")
    
    # Convert hourly to monthly
    hourly_mask = df['Salary'].str.contains('/h')
    if hourly_mask.sum() > 0:
        print(f"Converting {hourly_mask.sum()} hourly rates to monthly rates")
        df.loc[hourly_mask, 'min_salary'] = df.loc[hourly_mask, 'min_salary'] * 160
        df.loc[hourly_mask, 'max_salary'] = df.loc[hourly_mask, 'max_salary'] * 160
        df.loc[hourly_mask, 'avg_salary'] = df.loc[hourly_mask, 'avg_salary'] * 160
    
    return df

def extract_salary_range(salary_str):
    # Extract minimum and maximum salary
    if pd.isna(salary_str):
        return pd.NA, pd.NA
    
    # Extract just numbers with regex
    matches = re.findall(r'€?\s*(\d+(?:[\s,.]\d+)*)', salary_str)
    
    #problem to fix: only takes ranges (like 1000-2000), single values discarded
    if len(matches) >= 2:
        try:
            min_salary = float(matches[0].replace(' ', ''))
            max_salary = float(matches[1].replace(' ', ''))
            return min_salary, max_salary
        
        except ValueError:
            return pd.NA, pd.NA
        
    return pd.NA, pd.NA

def categorize_jobs(df):
    print("Categorizing job positions...")
    
    # Define job categories with relevant keywords (in English and Lithuanian)
    # ADD:
        # 1. AI engineer/DI inžinierius
        # 2. Cloud
        # 3. Categorize by programming language (Java, .NET, PHP) Mobile
        # 4. Web developer (frontend)
        # 5. Systems engineering/systems analysis (Oracle?)
    job_categories = {
        'Data Engineer': ['data engineer', 'duomenų inžinier', 'data hub', 'data solutions'],
        'Data Analyst': ['data analyst', 'duomenų anali', 'analitikas', 'analytics'],
        'Data Scientist': ['data scientist', 'duomenų moksli', 'ai engineer', 'machine learning'],
        'Software Developer': ['developer', 'programuotoj', 'software engineer', '.net', 'java', 'c++', 
                              'php', 'angular', 'react', 'full stack', 'fullstack', 'front-end', 'backend', 
                              'back-end', 'embedded', 'android', 'ios'],
        'DevOps': ['devops', 'sre', 'site reliability', 'cloud', 'platform engineer'],
        'QA Engineer': ['qa', 'test', 'quality', 'testuotoj'],
        'IT Support': ['support', 'pagalb', 'help desk', 'administrat', 'klient'],
        'Project Manager/Product Owner': ['project manager', 'projektų vadov', 'product owner', 'produkto vadov', 'produktų vadov', 'sprendimų vadov', 'komandos vadov'],
        'Business Analyst': ['business analyst', 'verslo anali', 'business intelligence'],
        'Security': ['security', 'saug', 'ciso', 'cyber'],
        'Database Admin': ['dba', 'database', 'sql', 'data manage'],
    }
    
    # Function to categorize a given job title
    def categorize_job(title):
        if pd.isna(title):
            return "Unknown"
        
        title_lower = title.lower()
        
        for category, keywords in job_categories.items():
            if any(keyword.lower() in title_lower for keyword in keywords):
                return category
        
        # Seniority indicators
        #if any(word in title_lower for word in ['senior', 'lead', 'head', 'chief', 'vyr']):   #COMMENTED THIS (REDUNDANT)
        #    return 'Senior/Lead Position'                          
            
        return 'Other'
    
    # Add seniority indicator (Junior, Mid, Senior)
    def detect_seniority(title):
        if pd.isna(title):
            return "Unknown"
            
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['junior', 'associate', 'entry', 'intern', 'stažuot', 'praktika', 'pradedant']):
            return 'Junior'
        elif any(word in title_lower for word in ['senior', 'vyr', 'lead', 'head', 'chief']):
            return 'Senior'
        elif any(word in title_lower for word in ['mid', 'intermediate']):
            return 'Mid'
        else:
            return 'Not Specified'
    
    # Categorization
    df['job_category'] = df['Title'].apply(categorize_job)
    df['seniority'] = df['Title'].apply(detect_seniority)
    
    print("Job Category Distribution:")
    category_counts = df['job_category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} positions")
    
    return df

def analyze_salaries(df):
    # Analyze salary statistics by job category
    
    print(f"\nOverall market statistics:")
    print(f"  Salary range: €{df['min_salary'].min():.0f} - €{df['max_salary'].max():.0f}")
    print(f"  Average salary: €{df['avg_salary'].mean():.0f}")
    print(f"  Median salary: €{df['avg_salary'].median():.0f}")
    
    # Group by job category and calculate stats
    salary_stats = df.groupby('job_category').agg({
        'min_salary': ['median', 'mean', 'min', 'max', 'count'],
        'max_salary': ['median', 'mean'],
        'avg_salary': ['median', 'mean']
    }).sort_values(('avg_salary', 'median'), ascending=False)
    
    print("\nSalary statistics by job category (sorted by median average salary):")
    for category in salary_stats.index:
        count = salary_stats.loc[category, ('min_salary', 'count')]
        if count < 5:  # Skip categories with too few data points, nice
            continue
            
        median_min = salary_stats.loc[category, ('min_salary', 'median')]
        median_max = salary_stats.loc[category, ('max_salary', 'median')]
        median_avg = salary_stats.loc[category, ('avg_salary', 'median')]
        
        print(f"\n  {category} ({int(count)} positions):")
        print(f"    Typical Range: €{median_min:.0f} - €{median_max:.0f}")
        print(f"    Median Salary: €{median_avg:.0f}")
    
    # Vy seniority
    seniority_stats = df.groupby('seniority').agg({
        'avg_salary': ['median', 'mean', 'min', 'max', 'count']
    }).sort_values(('avg_salary', 'median'))
    
    # PROBLEM 2!
    # Remove 'Not Specified' from the seniority stats
    print("\nSalary by Seniority Level:")
    for level in seniority_stats.index:
        count = seniority_stats.loc[level, ('avg_salary', 'count')]
        median = seniority_stats.loc[level, ('avg_salary', 'median')]
        print(f"  {level}: €{median:.0f} (median, {int(count)} positions)") 
    
    # Find highest paying job categories
    top_categories = salary_stats.head(5).index.tolist()
    print(f"\nTop 5 Highest Paying Job Categories (by median salary):")
    for i, category in enumerate(top_categories, 1):
        median = salary_stats.loc[category, ('avg_salary', 'median')]
        print(f"  {i}. {category}: €{median:.0f}")

def create_visualizations(df):
    print("\nGenerating visualizations...")
    
    # Filter categories with at least 5 entries for better visualization
    category_counts = df['job_category'].value_counts()
    valid_categories = category_counts[category_counts >= 5].index
    df_filtered = df[df['job_category'].isin(valid_categories)]
    
    # 1. Boxplot of salary distributions by job category
    plt.figure(figsize=(12, 8))
    box_plot = sns.boxplot(x='job_category', y='avg_salary', data=df_filtered, 
                          order=df_filtered.groupby('job_category')['avg_salary'].median().sort_values(ascending=False).index)
    plt.title('Salary Distributions by Job Category', fontsize=16)
    plt.xlabel('Job Category', fontsize=14)
    plt.ylabel('Average Salary (€)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('salary_distribution_by_category.png')
    print("  Saved 'salary_distribution_by_category.png'")
    plt.close()
    
    # USELESS FOR NOW
    # 2. Bar chart showing median salaries with error bars
    #plt.figure(figsize=(12, 8))
    #category_data = df_filtered.groupby('job_category').agg({
    #    'avg_salary': ['median', 'std', 'count']
    #}).sort_values(('avg_salary', 'median'), ascending=False)
    #
    #categories = category_data.index
    #medians = category_data[('avg_salary', 'median')].values
    #stds = category_data[('avg_salary', 'std')].values
    #counts = category_data[('avg_salary', 'count')].values
    #
    #std_errors = stds / np.sqrt(counts)
    #
    #plt.bar(categories, medians, yerr=std_errors, capsize=10, color='skyblue', alpha=0.8)
    #plt.title('Median Salary by Job Category', fontsize=16)
    #plt.xlabel('Job Category', fontsize=14)
    #plt.ylabel('Median Salary (€)', fontsize=14)
    #plt.xticks(rotation=45, ha='right')
    #plt.tight_layout()
    #plt.savefig('median_salary_by_category.png')
    #print("  Saved 'median_salary_by_category.png'")
    #plt.close()
    
    # 3. Seniority level comparison 
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='seniority', y='avg_salary', data=df, 
               order=['Junior', 'Mid', 'Senior', 'Not Specified'])
    plt.title('Salary Distribution by Seniority Level', fontsize=16)
    plt.xlabel('Seniority Level', fontsize=14)
    plt.ylabel('Average Salary (€)', fontsize=14)
    plt.tight_layout()
    plt.savefig('salary_by_seniority.png')
    print("  Saved 'salary_by_seniority.png'")
    plt.close()
    
    # USELESS FOR NOW
    # 4. Salary range distribution
    # plt.figure(figsize=(10, 6))
    # df['salary_range_pct'] = (df['salary_range'] / df['min_salary']) * 100
    # sns.histplot(df['salary_range_pct'].clip(0, 100), bins=20, kde=True)
    # plt.title('Salary Range Distribution (% above minimum)', fontsize=16)
    # plt.xlabel('Salary Range (% above minimum salary)', fontsize=14)
    # plt.ylabel('Count', fontsize=14)
    # plt.tight_layout()
    # plt.savefig('salary_range_distribution.png')
    # print("  Saved 'salary_range_distribution.png'")
    # plt.close()
    
    #PROBLEM 3!
    #STUPID LOOKING GRAPH
    # 5. Combined visualization - top 10 categories with seniority breakdown
    top_categories = df['job_category'].value_counts().head(10).index
    df_top = df[df['job_category'].isin(top_categories)]
    
    plt.figure(figsize=(14, 10))
    sns.boxplot(x='job_category', y='avg_salary', hue='seniority', data=df_top,
               order=df_top.groupby('job_category')['avg_salary'].median().sort_values(ascending=False).index)
    plt.title('Salary Distribution by Category and Seniority', fontsize=16)
    plt.xlabel('Job Category', fontsize=14)
    plt.ylabel('Average Salary (€)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Seniority')
    plt.tight_layout()
    plt.savefig('salary_by_category_and_seniority.png')
    print("  Saved 'salary_by_category_and_seniority.png'")
    plt.close()

if __name__ == "__main__":
    main()