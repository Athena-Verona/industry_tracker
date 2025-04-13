import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from collections import Counter

#plt.style.use('ggplot')
#sns.set_palette("viridis")

def main():
    print("Loading and analyzing job salary data...")
    
    try:
        df = pd.read_csv('analysis_CVonline/cvonline_jobs.csv', delimiter=';')
        print(f"Successfully loaded data with {len(df)} job listings")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    df = clean_data(df)
    df = categorize_jobs(df)
    analyze_salaries(df)
    create_visualizations(df)
    
    df.to_csv('analysis_CVonline/processed_salary_data.csv', index=False)
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
    
    job_categories = {
        'Project Manager/Product Owner': ['project manager', 'projektų vadov', 'projektų vadov',  'product owner', 
                                          'produkto vadov', 'produktų vadov', 'sprendimų vadov', 'komandos vadov', 'IT projekt'],
        'Python': ['python', 'python developer', 'python engineer', 'python inžinier'],
        'Data Engineer': ['data engineer', 'duomenų inžinier', 'data hub', 'data solutions', 'data manage'],
        'Back-end developer': ['back-end', 'backend', 'back end', 'php', 'back end engineer', 'node.js', 'ruby on rails', 'laravel', 'django', 'spring', 'flask'],
        'Data Analyst': ['data analyst', 'duomenų anali', 'analitikas', 'analytics'],
        '.NET Developer': ['.net', 'c#', 'asp.net', 'dotnet', 'dot net'],
        'Java Developer': ['java', 'java developer', 'java engineer', 'java inžinier'],
        'Data Scientist': ['data scientist', 'duomenų moksli', 'ai engineer', 'machine learning', 'di inžinier', 'mlops', 'dirbtinis intelektas'],
        'Front-end Web developer': ['web developer','react', 'angular', 'web designer', 'web design', 'frontend', 
                          'front end', 'front-end', 'ui/ux', 'user experience'],
        'Full-stack Developer': ['full stack', 'fullstack', 'full-stack'],
        'Mobile Developer': ['mobile dev', 'mobile engin', 'mobile inžinier', 'mobile app', 
                             'aplikacij', 'android', 'ios', 'apple', 'application dev', 'flutter', 'kotlin', 'swift'],
        'Embedded Developer': ['embedded', 'C++', 'įterptinių sistemų', 'įterptinės'],
        'Database Admin': ['dba', 'database', 'sql', 'oracle', 'postgresql', 'mysql'],
        'DevOps': ['devops', 'sre', 'site reliability', 'cloud', 'platform engineer', 'azure', 'aws', 'docker', 'kubernetes'],
        'Software Developer': ['developer', 'programuotoj', 'software engineer'],
        'QA Engineer': ['qa', 'test', 'quality', 'testuotoj'],
        'IT Support': ['support', 'pagalb', 'help desk', 'administrat', 'klient'],
        'Business Analyst': ['business analyst', 'verslo anali', 'business intelligence', 'BI'],
        'Security': ['security', 'saug', 'ciso', 'cyber', 'devsecops', 'infosec', 'information security'],
        'System Administrator/Architect': ['sysadmin', 'system administrator', 'linux', 'windows', 'unix', 'it administrator', 
                                           'sistemų administrator', 'sistemų architekt', 'system architect', 'system engineer', 'IS special'],
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
        
        if any(word in title_lower for word in ['junior', 'associate', 'entry', 'intern', 'stažuot', 'praktika', 'pradedan', 'graduate']):
            return 'Junior'
        elif any(word in title_lower for word in ['mid', 'intermediate']):
            return 'Mid'
        elif any(word in title_lower for word in ['senior', 'vyr', 'lead', 'head', 'chief', 'experienced', 'ekspert', 'expert']):
            return 'Senior'
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
    
    # Vyr seniority
    seniority_stats = df.groupby('seniority').agg({
        'avg_salary': ['median', 'mean', 'min', 'max', 'count']
    }).sort_values(('avg_salary', 'median'))
    
    # Remove not specified for now
    seniority_stats = seniority_stats.drop(index='Not Specified', errors='ignore')
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
    
    # Filter categories with at least 4 entries
    category_counts = df['job_category'].value_counts()
    valid_categories = category_counts[category_counts >= 4].index
    df_filtered = df[df['job_category'].isin(valid_categories)]
    
    # Plot of salary distributions by job category (many categories)
    plt.figure(figsize=(12, 8))
    box_plot = sns.boxplot(x='job_category', y='avg_salary', data=df_filtered, 
                          order=df_filtered.groupby('job_category')['avg_salary'].median().sort_values(ascending=False).index)
    plt.title('Salary Distributions by Job Category', fontsize=16)
    plt.xlabel('Job Category', fontsize=14)
    plt.ylabel('Average Salary (€)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('analysis_CVonline/salary_distribution_by_category.png')
    print("Saved 'salary_distribution_by_category.png'")
    plt.close()
    
    # Seniority level comparison 
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='seniority', y='avg_salary', data=df, 
               order=['Junior', 'Mid', 'Senior'])
    plt.title('Salary Distribution by Seniority Level', fontsize=16)
    plt.xlabel('Seniority Level', fontsize=14)
    plt.ylabel('Average Salary (€)', fontsize=14)
    plt.tight_layout()
    plt.savefig('analysis_CVonline/salary_by_seniority.png')
    print("Saved 'salary_by_seniority.png'")
    plt.close()

if __name__ == "__main__":
    main()