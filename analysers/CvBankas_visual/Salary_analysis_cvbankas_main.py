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
    print("Loading and analyzing cvbankas job salary data...")
    
    try:
        # Load data - adjust delimiter based on your file
        df = pd.read_csv('cvbankas_jobs.csv', delimiter=';')
        print(f"Successfully loaded data with {len(df)} job listings")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    df = clean_data(df)
    df = categorize_jobs(df)
    
    # Add a new column to identify IT vs non-IT jobs
    df = classify_it_jobs(df)
    
    # Display IT vs non-IT distribution
    it_count = df['is_it_job'].sum()
    non_it_count = len(df) - it_count
    print(f"\nJob Type Distribution:")
    print(f"  IT-related jobs: {it_count} ({it_count/len(df)*100:.1f}%)")
    print(f"  Non-IT jobs: {non_it_count} ({non_it_count/len(df)*100:.1f}%)")
    
    # Filter for IT jobs only for further analysis
    df_it = df[df['is_it_job'] == True].copy()
    print(f"\nFiltering to analyze only IT-related jobs: {len(df_it)} positions")
    
    # Run analysis and visualizations only on IT jobs
    analyze_salaries(df_it)
    create_visualizations(df_it)
    create_job_category_chart(df_it)
    
    # Save processed data
    df.to_csv('processed_cvbankas_data.csv', index=False)
    df_it.to_csv('processed_cvbankas_it_data.csv', index=False)
    print("Analysis complete!")

def clean_data(df):
    # Your existing clean_data function
    # ...
    
    # The rest of the function remains the same
    print("Cleaning and preparing data...")
    
    df = df.copy()
    
    # Print some data stats before cleaning
    print(f"Initial data shape: {df.shape}")
    print(f"Columns in dataset: {', '.join(df.columns)}")
    
    # Check for missing values in key columns
    missing_values = df.isnull().sum()
    print(f"Missing values before cleaning:\n{missing_values}")
    
    # Extract min and max salary from the Salary column
    df['min_salary'], df['max_salary'] = zip(*df['Salary'].apply(extract_salary_range))
    
    # Debug: print some extracted salary values to verify extraction is working
    print("\nSample of extracted salary values (first 5 rows):")
    for i, (salary_str, min_sal, max_sal) in enumerate(zip(df['Salary'].head(5), df['min_salary'].head(5), df['max_salary'].head(5))):
        print(f"  Row {i+1}: '{salary_str}' -> Min: {min_sal}, Max: {max_sal}")
    
    # Calculate average salary and salary range
    df['avg_salary'] = df.apply(lambda row: 
                               row['min_salary'] if pd.isna(row['max_salary']) else 
                               (row['min_salary'] + row['max_salary']) / 2, axis=1)
    df['salary_range'] = df.apply(lambda row: 
                                 0 if pd.isna(row['max_salary']) else 
                                 row['max_salary'] - row['min_salary'], axis=1)
    
    # Count how many single values vs ranges
    single_value_count = df['max_salary'].isna().sum()
    range_count = (~df['max_salary'].isna()).sum()
    print(f"\nSalary format distribution:")
    print(f"  Single value (e.g., 'From X'): {single_value_count} entries")
    print(f"  Salary range (e.g., 'X-Y'): {range_count} entries")
    
    # Remove rows with no salary info
    original_count = len(df)
    df = df.dropna(subset=['min_salary'])
    print(f"Removed {original_count - len(df)} rows with missing salary information")
    
    # Convert hourly to monthly (assuming 160 working hours per month)
    # Look for low salaries (likely hourly rates) or explicit hourly indicators
    hourly_indicators = ['/h', '€/h', '/hour', '/val']
    hourly_mask = df['Salary'].apply(lambda x: any(ind in str(x).lower() for ind in hourly_indicators) if not pd.isna(x) else False)
    
    # Also consider very low salaries (under 50) as likely hourly
    low_salary_mask = (df['min_salary'] < 50) & (~hourly_mask)
    
    total_hourly = hourly_mask.sum() + low_salary_mask.sum()
    if total_hourly > 0:
        print(f"Converting {total_hourly} hourly rates to monthly rates")
        print(f"  - {hourly_mask.sum()} explicit hourly rates")
        print(f"  - {low_salary_mask.sum()} implicitly detected hourly rates (values < 50)")
        
        # Convert explicit hourly rates
        if hourly_mask.sum() > 0:
            df.loc[hourly_mask, 'min_salary'] = df.loc[hourly_mask, 'min_salary'] * 160
            df.loc[hourly_mask, 'max_salary'] = df.loc[hourly_mask, 'max_salary'].fillna(df.loc[hourly_mask, 'min_salary']) * 160
            df.loc[hourly_mask, 'avg_salary'] = df.loc[hourly_mask, 'avg_salary'] * 160
        
        # Convert implicit hourly rates (very low values)
        if low_salary_mask.sum() > 0:
            df.loc[low_salary_mask, 'min_salary'] = df.loc[low_salary_mask, 'min_salary'] * 160
            df.loc[low_salary_mask, 'max_salary'] = df.loc[low_salary_mask, 'max_salary'].fillna(df.loc[low_salary_mask, 'min_salary']) * 160
            df.loc[low_salary_mask, 'avg_salary'] = df.loc[low_salary_mask, 'avg_salary'] * 160
    
    # Summary statistics after cleaning
    print(f"\nSalary statistics after cleaning:")
    print(f"  Min salary range: €{df['min_salary'].min():.0f} - €{df['max_salary'].max() if not pd.isna(df['max_salary'].max()) else df['min_salary'].max():.0f}")
    print(f"  Average salary: €{df['avg_salary'].mean():.0f}")
    
    return df

def extract_salary_range(salary_str):
    # Your existing extract_salary_range function remains unchanged
    """Extract minimum and maximum salary from salary string"""
    if pd.isna(salary_str):
        return pd.NA, pd.NA
    
    salary_str = str(salary_str).strip()
    
    # Handle "From X" or "Nuo X" format
    from_patterns = [r'From\s+(\d+(?:[\s,.]\d+)*)', r'Nuo\s+(\d+(?:[\s,.]\d+)*)', r'^(\d+(?:[\s,.]\d+)*)$']
    
    for pattern in from_patterns:
        from_match = re.search(pattern, salary_str)
        if from_match:
            min_value = float(from_match.group(1).replace(' ', '').replace(',', '.'))
            return min_value, pd.NA
    
    # Handle range format (e.g., "1200-2300")
    range_patterns = [
        r'(\d+(?:[\s,.]\d+)*)\s*-\s*(\d+(?:[\s,.]\d+)*)',  # Standard range
        r'(\d+(?:[\s,.]\d+)*)\s*–\s*(\d+(?:[\s,.]\d+)*)',  # Em dash
        r'(\d+(?:[\s,.]\d+)*)\s*to\s*(\d+(?:[\s,.]\d+)*)'  # "to" keyword
    ]
    
    for pattern in range_patterns:
        range_match = re.search(pattern, salary_str)
        if range_match:
            min_value = float(range_match.group(1).replace(' ', '').replace(',', '.'))
            max_value = float(range_match.group(2).replace(' ', '').replace(',', '.'))
            return min_value, max_value
    
    # Handle any other numeric values (just extract the first number found)
    numbers = re.findall(r'(\d+(?:[\s,.]\d+)*)', salary_str)
    if numbers:
        try:
            value = float(numbers[0].replace(' ', '').replace(',', '.'))
            return value, pd.NA  # Return as min only
        except (ValueError, IndexError):
            pass
    
    return pd.NA, pd.NA

def categorize_jobs(df):
    # Your existing categorize_jobs function remains largely the same
    print("Categorizing job positions...")
    
    # Define job categories with relevant keywords (in English and Lithuanian)
    job_categories = {
        'IT Management': ['it vadov', 'it manager', 'cio', 'project manager', 'projektų vadov', 'product owner', 
                          'produkto vadov', 'scrum master', 'agile coach', 'komandos vadov', 'sprendimų vadov'],
        'Software Development': ['developer', 'programuotoj', 'software engineer', 'kūrėj', 'full stack', 
                                'fullstack', 'front-end', 'frontend', 'back-end', 'backend', '.net', 'java', 
                                'c++', 'c#', 'php', 'python', 'javascript', 'angular', 'react', 'node'],
        'Data & Analytics': ['data', 'duomen', 'analyst', 'anali', 'scientist', 'moksli', 'bi ', 'business intelligence', 
                             'statist', 'database', 'duomenų baz'],
        'DevOps & Systems': ['devops', 'sre', 'system', 'admin', 'cloud', 'aws', 'azure', 'infrastruktūr', 'network', 'tinkl'],
        'QA & Testing': ['qa', 'test', 'quality', 'kokyb', 'testuotoj'],
        'Security': ['security', 'saug', 'cyber', 'ciber'],
        'Design & UI/UX': ['design', 'dizain', 'ui', 'ux', 'user experience', 'user interface', 'graphic', 'grafik'],
        'Mobile Development': ['mobile', 'mobil', 'android', 'ios', 'app', 'aplikacij'],
        'Sales & Customer Service': ['sales', 'pardavim', 'klientų aptarnavim', 'customer', 'konsultant', 'vadybinink'],
        'Marketing & Communications': ['market', 'rink', 'komunikacij', 'communi', 'pr ', 'public relations', 'ryšiai su visuomene'],
        'Finance & Accounting': ['financ', 'finans', 'accounting', 'apskait', 'buhalter', 'ekonom'],
        'HR & Administration': ['hr', 'human resources', 'personalo', 'personalas', 'žmogiškieji ištekliai', 'admin', 'asistent', 'office'],
        'Manufacturing & Production': ['gamyb', 'production', 'manufact', 'operator', 'technolog', 'inžinier'],
        'Logistics & Transport': ['logist', 'transport', 'vairuotoj', 'driver', 'kurjer', 'courier', 'sandėl', 'warehouse'],
        'Healthcare & Medical': ['health', 'sveikat', 'medic', 'slaugytoj', 'nurse', 'gydytoj', 'doctor'],
        'Engineering': ['engineer', 'inžinier', 'technolog', 'technik', 'mechanics', 'mechanik'],
        'Management': ['manager', 'vadov', 'director', 'direktorius', 'vadyba'],
        'Maintenance': ['maintenance', 'priežiūr', 'repair', 'remont', 'ūkvedys'],
        'Cleaning & Facilities': ['clean', 'valytoj', 'facilities', 'patalpų priežiūr', 'valymo'],
        'Retail': ['retail', 'mažmeninė prekyba', 'pardavėj', 'kasininkas', 'cashier', 'shop', 'parduotuvė'],
        'Construction': ['construction', 'statyb', 'statybos'],
        'Legal': ['legal', 'teis', 'advokat', 'jurist'],
        'Food Service': ['food', 'maisto', 'chef', 'virėj', 'restorano', 'restoran', 'barista', 'barmen'],
        'Education': ['education', 'švietim', 'teach', 'mokytoj', 'lecturer', 'dėstytoj'],
    }
    
    # Function to categorize a job title
    def categorize_job(title, company=None):
        if pd.isna(title):
            return "Unknown"
        
        # Combine title and company for better categorization if company info is available
        text_to_check = (str(title) + ' ' + str(company if not pd.isna(company) else '')).lower()
        
        for category, keywords in job_categories.items():
            if any(keyword.lower() in text_to_check for keyword in keywords):
                return category
                
        return 'Other'
    
    # Detect seniority from job title
    def detect_seniority(title):
        if pd.isna(title):
            return "Unknown"
            
        title_lower = str(title).lower()
        
        # Junior indicators
        if any(word in title_lower for word in ['junior', 'jaunesnysis', 'associate', 'entry', 'intern', 'stažuot', 'praktika', 'pradedant']):
            return 'Junior'
        # Senior indicators
        elif any(word in title_lower for word in ['senior', 'vyr', 'lead', 'head', 'chief', 'vyriausias', 'vadovaujantis']):
            return 'Senior'
        # Mid-level indicators
        elif any(word in title_lower for word in ['mid', 'middle', 'intermediate', 'specialist']):
            return 'Mid'
        # Default case
        else:
            return 'Other'  # Changed from 'Not Specified' to 'Other'
    
    # Apply categorization
    df['job_category'] = df.apply(lambda row: categorize_job(row['Title'], row.get('Company')), axis=1)
    df['seniority'] = df['Title'].apply(detect_seniority)
    
    # Display distribution of seniority levels
    print("\nSeniority Level Distribution:")
    seniority_counts = df['seniority'].value_counts()
    for level, count in seniority_counts.items():
        print(f"  {level}: {count} positions ({count/len(df)*100:.1f}%)")
    
    # Display distribution of job categories
    print("\nJob Category Distribution:")
    category_counts = df['job_category'].value_counts()
    for category, count in category_counts.nlargest(10).items():
        print(f"  {category}: {count} positions ({count/len(df)*100:.1f}%)")
    
    if len(category_counts) > 10:
        print(f"  ... and {len(category_counts) - 10} more categories")
    
    return df

def classify_it_jobs(df):
    """Add a new column to identify if a job is IT-related"""
    print("\nClassifying IT vs non-IT jobs...")
    
    # Define IT-related categories
    it_categories = [
        'IT Management', 
        'Software Development', 
        'Data & Analytics', 
        'DevOps & Systems', 
        'QA & Testing', 
        'Security', 
        'Design & UI/UX', 
        'Mobile Development'
    ]
    
    # Additional IT-related keywords that might appear in job titles but not caught by categories
    it_keywords = [
        'it ', 'programmer', 'developer', 'software', 'web', 'programuotoj', 
        'system', 'network', 'cyber', 'database', 'data', 'analyst', 'analytics',
        'devops', 'cloud', 'security', 'ai', 'machine learning', 'computer',
        'tech', 'technolog', 'coder', 'coding', 'engineer', 'engineerin'
    ]
    
    # Function to check if a job is IT-related
    def is_it_job(row):
        # First check category
        if row['job_category'] in it_categories:
            return True
        
        # Then check title for IT keywords
        title = str(row['Title']).lower() if not pd.isna(row['Title']) else ""
        if any(keyword in title for keyword in it_keywords):
            return True
        
        # Check company name for IT keywords (optional)
        company = str(row.get('Company', '')).lower() if not pd.isna(row.get('Company', '')) else ""
        if any(keyword in company for keyword in ['tech', 'soft', 'it ', 'digital', 'data', 'cyber', 'web']):
            return True
            
        return False
    
    # Apply the function to create a new column
    df['is_it_job'] = df.apply(is_it_job, axis=1)
    
    return df

def analyze_salaries(df):
    # Your existing analyze_salaries function
    # Analyze salary statistics by job category
    
    print(f"\nOverall market statistics:")
    print(f"  Salary range: €{df['min_salary'].min():.0f} - €{df['max_salary'].max() if not pd.isna(df['max_salary'].max()) else df['min_salary'].max():.0f}")
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
        if count < 5:  # Skip categories with too few data points
            continue
            
        median_min = salary_stats.loc[category, ('min_salary', 'median')]
        
        if not pd.isna(salary_stats.loc[category, ('max_salary', 'median')]):
            median_max = salary_stats.loc[category, ('max_salary', 'median')]
            range_str = f"€{median_min:.0f} - €{median_max:.0f}"
        else:
            range_str = f"From €{median_min:.0f}"
            
        median_avg = salary_stats.loc[category, ('avg_salary', 'median')]
        
        print(f"\n  {category} ({int(count)} positions):")
        print(f"    Typical Range: {range_str}")
        print(f"    Median Salary: €{median_avg:.0f}")
    
    # By seniority - include 'Other' category
    seniority_stats = df.groupby('seniority').agg({
        'avg_salary': ['median', 'mean', 'min', 'max', 'count'],
        'min_salary': ['median', 'count'],
    }).sort_values(('avg_salary', 'median'))
    
    print("\nSalary by Seniority Level:")
    for level in seniority_stats.index:
        count = seniority_stats.loc[level, ('min_salary', 'count')]
        median = seniority_stats.loc[level, ('avg_salary', 'median')]
        mean = seniority_stats.loc[level, ('avg_salary', 'mean')]
        print(f"  {level}: €{median:.0f} (median), €{mean:.0f} (mean), {int(count)} positions")
    
    # Find highest paying job categories
    top_categories = salary_stats.head(5).index.tolist()
    print(f"\nTop 5 Highest Paying Job Categories (by median salary):")
    for i, category in enumerate(top_categories, 1):
        median = salary_stats.loc[category, ('avg_salary', 'median')]
        count = salary_stats.loc[category, ('min_salary', 'count')]
        print(f"  {i}. {category}: €{median:.0f} ({int(count)} positions)")
    
    # Special analysis: Senior vs Junior salary gap by category
    print("\nSenior vs Junior salary gap by category:")
    
    # Get categories with both senior and junior positions
    categories_with_both = []
    for category in df['job_category'].unique():
        senior_count = len(df[(df['job_category'] == category) & (df['seniority'] == 'Senior')])
        junior_count = len(df[(df['job_category'] == category) & (df['seniority'] == 'Junior')])
        if senior_count >= 3 and junior_count >= 3:
            categories_with_both.append(category)
    
    if len(categories_with_both) > 0:
        for category in categories_with_both:
            senior_median = df[(df['job_category'] == category) & (df['seniority'] == 'Senior')]['avg_salary'].median()
            junior_median = df[(df['job_category'] == category) & (df['seniority'] == 'Junior')]['avg_salary'].median()
            gap_pct = ((senior_median / junior_median) - 1) * 100
            senior_count = len(df[(df['job_category'] == category) & (df['seniority'] == 'Senior')])
            junior_count = len(df[(df['job_category'] == category) & (df['seniority'] == 'Junior')])
            
            print(f"  {category}: Senior €{senior_median:.0f} vs Junior €{junior_median:.0f} " +
                  f"(+{gap_pct:.1f}%, {senior_count} Sr / {junior_count} Jr positions)")
    else:
        print("  Not enough data for reliable senior/junior comparison in any category")

def create_visualizations(df):
    # Your existing create_visualizations function, but working on IT-filtered data
    print("\nGenerating visualizations...")
    
    # Filter categories with at least 5 entries for better visualization
    category_counts = df['job_category'].value_counts()
    valid_categories = category_counts[category_counts >= 5].index
    df_filtered = df[df['job_category'].isin(valid_categories)]
    
    print(f"Using {len(df_filtered)} entries (from {len(valid_categories)} categories) for visualizations")
    
    # 1. Boxplot of salary distributions by job category (top 12 categories)
    plt.figure(figsize=(16, 10))
    # Get the top 12 categories by count
    top_categories = df['job_category'].value_counts().head(12).index
    df_top = df[df['job_category'].isin(top_categories)]
    
    if len(df_top) > 0:
        box_plot = sns.boxplot(x='job_category', y='avg_salary', data=df_top, 
                            order=df_top.groupby('job_category')['avg_salary'].median().sort_values(ascending=False).index)
        plt.title('IT Job Salary Distributions by Category (Top 12)', fontsize=16)
        plt.xlabel('Job Category', fontsize=14)
        plt.ylabel('Average Salary (€)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('cvbankas_it_salary_by_category.png')
        print("  Saved 'cvbankas_it_salary_by_category.png'")
    plt.close()
    
    # 2. Seniority level comparison - include 'Other' category
    plt.figure(figsize=(12, 8))
    # Use all seniority levels
    order = ['Junior', 'Mid', 'Senior', 'Other']
    # Only include levels that exist in the data
    existing_levels = [level for level in order if level in df['seniority'].unique()]
    
    if len(existing_levels) > 1:
        senior_data = df[df['seniority'].isin(existing_levels)]
        sns.boxplot(x='seniority', y='avg_salary', data=senior_data, order=existing_levels)
        plt.title('IT Job Salary Distribution by Seniority Level', fontsize=16)
        plt.xlabel('Seniority Level', fontsize=14)
        plt.ylabel('Average Salary (€)', fontsize=14)
        plt.tight_layout()
        plt.savefig('cvbankas_it_salary_by_seniority.png')
        print("  Saved 'cvbankas_it_salary_by_seniority.png'")
    else:
        print("  Not enough seniority data for visualization")
    plt.close()
    
    # 3. Cities/locations comparison
    plt.figure(figsize=(14, 8))
    location_counts = df['Location'].value_counts()
    top_locations = location_counts[location_counts >= 8].index  # At least 8 entries per location
    
    if len(top_locations) > 1:
        loc_data = df[df['Location'].isin(top_locations)]
        loc_order = loc_data.groupby('Location')['avg_salary'].median().sort_values(ascending=False).index
        
        sns.boxplot(x='Location', y='avg_salary', data=loc_data, order=loc_order)
        plt.title('IT Job Salary Distribution by Location', fontsize=16)
        plt.xlabel('Location', fontsize=14)
        plt.ylabel('Average Salary (€)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('cvbankas_it_salary_by_location.png')
        print("  Saved 'cvbankas_it_salary_by_location.png'")
    else:
        print("  Not enough location data for visualization")
    plt.close()
    
    # 5. Histogram of salary ranges
    plt.figure(figsize=(12, 8))
    # Only include entries with both min and max salary
    salary_range_data = df[df['max_salary'].notna()]
    
    if len(salary_range_data) > 10:
        salary_range_pct = salary_range_data['salary_range'] / salary_range_data['min_salary'] * 100
        sns.histplot(salary_range_pct.clip(0, 150), bins=20, kde=True)
        plt.title('IT Job Salary Range Distribution (% above minimum)', fontsize=16)
        plt.xlabel('Salary Range (% above minimum salary)', fontsize=14)
        plt.ylabel('Count', fontsize=14)
        plt.tight_layout()
        plt.savefig('cvbankas_it_salary_range_distribution.png')
        print("  Saved 'cvbankas_it_salary_range_distribution.png'")
    else:
        print("  Not enough salary range data for histogram")
    plt.close()

def create_job_category_chart(df):
    # Job category distribution pie chart for IT jobs only
    plt.figure(figsize=(12, 12))
    top_cats = df['job_category'].value_counts().head(8)
    other_count = df['job_category'].value_counts().iloc[8:].sum()
    
    # Combine top categories with "Other"
    if other_count > 0:
        data = pd.concat([top_cats, pd.Series({'Other categories': other_count})])
    else:
        data = top_cats
    
    # Use a color palette with enough distinct colors
    import matplotlib.cm as cm
    colors = cm.tab20(range(len(data)))
    # Make the "Other categories" a distinctive color (like gray)
    if other_count > 0:
        colors[-1] = [0.7, 0.7, 0.7, 1.0]  # Gray color for "Other categories"
    
    plt.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90, shadow=True, colors=colors)
    plt.axis('equal')
    plt.title('IT Job Category Distribution', fontsize=16)
    plt.tight_layout()
    plt.savefig('cvbankas_it_category_distribution.png')
    print("  Saved 'cvbankas_it_category_distribution.png'")
    plt.close()

if __name__ == "__main__":
    main()