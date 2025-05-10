import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
import jinja2
import base64
from io import BytesIO

from matplotlib.path import Path
from matplotlib.patches import PathPatch

from matplotlib.lines import Line2D
import matplotlib.patches as patches

class SalaryNewsletter:


    def __init__(self, data_file='processed_mega_dataset.csv'):
        """Initialize the newsletter generator with data file path"""
        self.data_file = data_file
        self.df = None
        self.template_dir = 'newsletter_templates'
        self.output_dir = 'newsletter_output'
        self.image_dir = 'newsletter_images'
        self.logo_dir = 'images'  # New directory for custom images like logo
        
        # Create necessary directories
        for directory in [self.template_dir, self.output_dir, self.image_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Create or update default template
        template_updated = self._create_default_template()
        if template_updated:
            print("Template was created or updated to match the current code definition.")

        # Add this method to your class to handle the logo
    def add_company_logo(self, logo_path=None):
        """Add a company logo to the newsletter
        
        Args:
            logo_path: Path to the logo image file. If None, a placeholder will be used.
        """
        # Default logo path in the logo directory
        default_logo = os.path.join(self.logo_dir, 'default_logo.png')
        
        if logo_path is None:
            # Create a simple placeholder logo if none provided
            if not os.path.exists(default_logo):
                plt.figure(figsize=(3, 2))
                plt.text(0.5, 0.5, 'Company\nLogo', 
                        horizontalalignment='center', 
                        verticalalignment='center', 
                        fontsize=20,
                        color='#3b74d9',
                        fontweight='bold')
                plt.axis('off')
                plt.tight_layout()
                plt.savefig(default_logo)
                plt.close()
            
            self.logo_path = default_logo
        else:
            # Use the provided logo
            self.logo_path = logo_path
        
        return self.logo_path

    def _create_default_template(self):
        """Create a default newsletter template if none exists or update if it differs"""
        template_path = os.path.join(self.template_dir, 'simple_template.html')
        
        # Define the current template HTML
        template_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ newsletter_title }}</title>
    <style>
        body {
            font-family: Inter, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 650px;
            margin: 0 auto;
            padding: 0;
            background-color: #f9f9f9;
            font-size: 20px;
            font-weight: 700;
        }

        p {
            font-size: 18px; 
            line-height: 1.6;
            margin-bottom: 16px;
        }
        .container {
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .header {
            background-color: #ffffff;
            color: #333;
            padding: 20px;
            text-align: left;
            border-bottom: 1px solid #eaeaea;
        }
        .welcome-text {
            font-size: 20px;
            margin-bottom: 5px;
            font-weight: 500;
        }
        .title {
            color: #3b74d9;
            font-size: 25px;
            font-weight: bold;
            margin: 5px 0;
        }
        .subtitle {
            font-size: 15px;
            margin-top: 5px;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .content {
            padding: 20px;
        }
        .highlights {
            background-color: #f0f6ff !important;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .highlights-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .highlight-item {
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
        }
        .highlight-icon {
            width: 24px;
            height: 24px;
            margin-right: 10px;
            color: #3b74d9;
            flex-shrink: 0;
        }
        .highlight-text {
            flex-grow: 1;
            font-size: 17px;
            font-weight: 500;
        }
        .highlight-label {
            color: #3b74d9;
            font-weight: bold;
            margin-right: 5px;
            font-size: 17px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .subsection-title {
            color: #3b74d9;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .footer {
            background-color: #f1f1f1;
            padding: 15px;
            text-align: center;
            font-size: 10px;
            color: #777;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .chart {
            margin: 20px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .top-bar {
            position: relative;
            margin-bottom: 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .line {
            border-top: 1px solid #000;
            width: 80%;
            height: 1px;
            margin-top: 80px;
        }

        .top-logo {
            background-color: white;
            padding: 0 10px;
            height: 150px; /* adjust as needed */
            display: flex;
            align-items: right;
            margin-left: 100px; /* space between line and logo */
        }



        

</style>
</head>
<body>
    <div class="container">
            <div class="header">
                <div class="top-bar">
                    <div class="line"></div>
                    <img src="cid:company_logo" alt="Company Logo" class="top-logo">
                </div>
                <h3 class="welcome-text">Welcome back</h3>
                <h1 class="title">{{ newsletter_title }}</h1>
                <p class="subtitle">{{ newsletter_date }}</p>
                <p>Stay informed with the latest hiring trends, tech stacks, and salary insights across the Baltics.</p>
                </div>
        </div>
        
        <div class="content">
            <div class="highlights">
                                <div class="highlight-item">
                    <div class="highlight-icon">
                        <img src="cid:binocular" alt="Binocular">
                    </div>
                    <div class="highlight-text">
                        <span class="highlight-label">Most In-Demand Role:</span>
                        <span>{{ most_demand_role }}</span>
                    </div>
                </div>

                <div class="highlight-item">
                    <div class="highlight-icon">
                        <img src="cid:iris_scan" alt="Iris Scan">
                    </div>
                    <div class="highlight-text">
                        <span class="highlight-label">Top Hiring Company:</span>
                        <span>{{ top_hiring_company }}</span>
                    </div>
                </div>

                <div class="highlight-item">
                    <div class="highlight-icon">
                        <img src="cid:splitting" alt="Splitting">
                    </div>
                    <div class="highlight-text">
                        <span class="highlight-label">Notable Market Move:</span>
                        <span>{{ notable_market_move }}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="line"></div>
                <h2 class="section-title">Trends This Month</h2>
                <h3 class="subsection-title">Top Roles In Demand</h3>
                
                <div class="chart">
                    <img src="cid:top_roles_chart" alt="Top Roles In Demand">
                </div>
                <p>The chart above shows the top roles in demand based on position frequency.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Top 5 Highest Paying Job Categories</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Job Category</th>
                        <th>Median Salary</th>
                    </tr>
                    {% for category in top_categories %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td>{{ category.name }}</td>
                        <td>€{{ category.median_salary }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2 class="section-title">Salary by Seniority</h2>
                <div class="chart">
                    <img src="cid:salary_seniority" alt="Salary by Seniority Level">
                </div>
                <table>
                    <tr>
                        <th>Seniority Level</th>
                        <th>Median Salary</th>
                        <th>Count</th>
                    </tr>
                    {% for level in seniority_levels %}
                    <tr>
                        <td>{{ level.name }}</td>
                        <td>€{{ level.median_salary }}</td>
                        <td>{{ level.count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p1>This newsletter is generated automatically based on Baltic IT job market data.</p1>
            <p1>To unsubscribe, please reply with "UNSUBSCRIBE" in the subject line.</p1>
        </div>
    </div>
</body>
</html>"""
        
        template_updated = False
        
        # Check if the template file exists
        if os.path.exists(template_path):
            # Read existing template
            with open(template_path, 'r', encoding='utf-8') as f:
                existing_template = f.read()
            
            # Compare and update if different
            if existing_template != template_html:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(template_html)
                print(f"Updated existing template at {template_path}")
                template_updated = True
        else:
            # Create new template file
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_html)
            print(f"Created default template at {template_path}")
            template_updated = True
        
        return template_updated
    
    def update_template(self, template_name='simple_template.html'):
        """
        Update the template file with the current template defined in the code.
        Returns True if the template was updated, False otherwise.
        """
        return self._create_default_template()
    
    def load_data(self):
        """Load and prepare the salary data"""
        try:
            self.df = pd.read_csv(self.data_file)
            print(f"Successfully loaded data with {len(self.df)} job listings")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_visualizations(self):
        """Generate visualizations for the newsletter"""
        if self.df is None:
            print("No data loaded. Please call load_data() first.")
            return
        
        # Create directory for visualizations
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Generate salary distribution chart
        plt.figure(figsize=(12, 8))
        # Filter categories with at least 4 entries
        category_counts = self.df['job_category'].value_counts()
        valid_categories = category_counts[category_counts >= 4].index
        df_filtered = self.df[self.df['job_category'].isin(valid_categories)]
        
        sns.boxplot(x='job_category', y='avg_salary', data=df_filtered, 
                   order=df_filtered.groupby('job_category')['avg_salary'].median().sort_values(ascending=False).index)
        plt.title('Salary Distributions by Job Category', fontsize=16)
        plt.xlabel('Job Category', fontsize=14)
        plt.ylabel('Average Salary (€)', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save as image file and as bytes for email embedding
        salary_dist_path = os.path.join(self.image_dir, 'salary_distribution.png')
        plt.savefig(salary_dist_path)
        
        salary_dist_buffer = BytesIO()
        plt.savefig(salary_dist_buffer, format='png')
        salary_dist_buffer.seek(0)
        plt.close()
        
# This code should replace the "Generate seniority level chart" section in your generate_visualizations method

        # Generate seniority level chart with improved design
        plt.figure(figsize=(10, 6))

        # Filter for valid seniority data
        valid_seniority = ['Junior', 'Mid', 'Senior']
        df_seniority = self.df[self.df['seniority'].isin(valid_seniority)]

        # Calculate statistics for each seniority level
        seniority_stats = {}
        for level in valid_seniority:
            level_data = df_seniority[df_seniority['seniority'] == level]
            if not level_data.empty:
                q1 = level_data['avg_salary'].quantile(0.25)
                median = level_data['avg_salary'].median()
                q3 = level_data['avg_salary'].quantile(0.75)
                mean = level_data['avg_salary'].mean()
                seniority_stats[level] = {
                    'q1': q1,
                    'median': median,
                    'q3': q3,
                    'mean': mean
                }

        # Set up the plot with soft background
        ax = plt.gca()
        ax.set_facecolor('#ffffff')
        fig = plt.gcf()
        fig.patch.set_facecolor('#ffffff')

        # Create positions for the bars
        positions = range(len(valid_seniority))
        bar_width = 0.6

        # Draw IQR background first
        for i, level in enumerate(valid_seniority):
            if level in seniority_stats:
                stats = seniority_stats[level]
                # IQR background as light blue rectangle
                iqr_height = stats['q3'] - stats['q1']
                iqr_rect = patches.Rectangle(
                    (i - bar_width/2, stats['q1']), 
                    bar_width, 
                    iqr_height,
                    facecolor='#f0f7ff',
                    edgecolor='none',
                    alpha=0.8,
                    zorder=1
                )
                ax.add_patch(iqr_rect)

        # Draw mean as horizontal lines
        for i, level in enumerate(valid_seniority):
            if level in seniority_stats:
                stats = seniority_stats[level]
                # Mean line as cyan
                plt.plot(
                    [i - bar_width/2 - 0.1, i + bar_width/2 + 0.1],
                    [stats['mean'], stats['mean']],
                    color='#36B3C9',
                    linewidth=2,
                    zorder=4
                )

        # Draw median as blue squares
        for i, level in enumerate(valid_seniority):
            if level in seniority_stats:
                stats = seniority_stats[level]
                # Median as blue square
                square_size = bar_width * 0.4
                median_rect = patches.Rectangle(
                    (i - square_size/2, stats['median'] - square_size/2 * stats['median']/1000), 
                    square_size, 
                    square_size * stats['median']/1000,
                    facecolor='#2D7FF9',
                    edgecolor='none',
                    zorder=5
                )
                ax.add_patch(median_rect)

        # Set up the axis
        plt.xlim(-0.5, len(valid_seniority) - 0.5)
        max_salary = max([stats['q3'] for level, stats in seniority_stats.items()]) * 1.2
        plt.ylim(0, max_salary)
        plt.xticks(positions, valid_seniority, fontsize=12)
        plt.yticks(fontsize=12)
        plt.ylabel('EUR', fontsize=14)

        # Add legend
        legend_elements = [
            patches.Rectangle((0, 0), 1, 1, facecolor='#2D7FF9', label='Median'),
            patches.Rectangle((0, 0), 1, 1, facecolor='#f0f7ff', label='IQR'),
            Line2D([0], [0], color='#36B3C9', lw=2, label='Average*')
        ]
        plt.legend(handles=legend_elements, loc='upper left', frameon=True, framealpha=1, 
                facecolor='#f9f9f9', edgecolor='#eeeeee')

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Add subtle grid lines
        plt.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)


        plt.tight_layout()

        # Save as image file and as bytes for email embedding
        salary_seniority_path = os.path.join(self.image_dir, 'salary_seniority.png')
        plt.savefig(salary_seniority_path, dpi=120, bbox_inches='tight')

        salary_seniority_buffer = BytesIO()
        plt.savefig(salary_seniority_buffer, format='png', dpi=120, bbox_inches='tight')
        salary_seniority_buffer.seek(0)
        plt.close()

        # In the generate_visualizations method:
        # Get top 5 roles by count
        if 'job_category' in self.df.columns:
            # Filter out "other" category before counting
            filtered_df = self.df[~self.df['job_category'].str.lower().isin(['other', 'others'])]
            role_counts = filtered_df['job_category'].value_counts().head(5)
            roles = role_counts.index.tolist()
            counts = role_counts.values.tolist()

            # Create figure
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            
            # Set up background with soft rounded corners
            height = max(counts) * 1.2
            width = len(roles) + 0.5
            
            # Round the corners of the background 
            from matplotlib.patches import FancyBboxPatch
            background = FancyBboxPatch(
                (-0.5, 0), width, height,
                boxstyle=f"round,pad=0,rounding_size={0.05*width}",
                facecolor='#f0f6ff', alpha=0.5, edgecolor='none', zorder=0
            )
            ax.add_patch(background)
            
            # Create normal bars first
            bars = ax.bar(range(len(roles)), counts, width=0.7, color='#2D7FF9', zorder=2)
            
            # Round the top corners with a simpler approach
            for bar in bars:
                x = bar.get_x()
                y = bar.get_height()
                width = bar.get_width()
                
                # Add rounded caps at the top of each bar
                radius = 0.15  # Radius for rounded corners
                
                # Create a rectangle with rounded corners for the top part
                from matplotlib.patches import Rectangle
                bar_top = FancyBboxPatch(
                    (x, y - radius), width, radius * 2,
                    boxstyle=f"round,pad=0,rounding_size={radius}",
                    facecolor='#2D7FF9', edgecolor='none', zorder=3
                )
                ax.add_patch(bar_top)
            
            # Set up the axis
            ax.set_xlim(-0.5, len(roles) - 0.5)
            ax.set_ylim(0, max(counts) * 1.2)  # Add some space at the top
            ax.set_xticks(range(len(roles)))
            
            # Set x-tick labels to job category name + count
            ax.set_xticklabels([f"{role} ({count})" for role, count in zip(roles, counts)], rotation=0)
            
            # Remove the vertical y-axis label and place horizontally at the top
            ax.set_ylabel('')  # Remove the default y-axis label
            ax.text(-0.4, max(counts) * 1.1, 'Job Postings', fontsize=18, ha='left')
            
            # Remove spines/borders
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            
            plt.tight_layout()
            
            # Save as image file and bytes for email embedding
            top_roles_path = os.path.join(self.image_dir, 'top_roles_chart.png')
            plt.savefig(top_roles_path)
            
            top_roles_buffer = BytesIO()
            plt.savefig(top_roles_buffer, format='png')
            top_roles_buffer.seek(0)
            plt.close()

        return {
            'salary_seniority': {
                'path': salary_seniority_path,
                'buffer': salary_seniority_buffer
            },
            'top_roles_chart': {
                'path': top_roles_path,
                'buffer': top_roles_buffer
            }
        }
    
    def prepare_newsletter_data(self):
        """Prepare all the data needed for the newsletter"""
        if self.df is None:
            print("No data loaded. Please call load_data() first.")
            return None
        
        # Create visualizations
        visualizations = self.generate_visualizations()
        
        # Check if required columns exist and handle missing columns gracefully
        required_salary_columns = ['min_salary', 'max_salary', 'avg_salary']
        for col in required_salary_columns:
            if col not in self.df.columns:
                print(f"Warning: Column '{col}' not found in data. Using placeholder values.")
                self.df[col] = 0
        
        # Overall market statistics
        overall_stats = {
            'min_salary': f"€{self.df['min_salary'].min():.0f}" if 'min_salary' in self.df.columns else "N/A",
            'max_salary': f"€{self.df['max_salary'].max():.0f}" if 'max_salary' in self.df.columns else "N/A",
            'avg_salary': f"€{self.df['avg_salary'].mean():.0f}" if 'avg_salary' in self.df.columns else "N/A",
            'median_salary': f"€{self.df['avg_salary'].median():.0f}" if 'avg_salary' in self.df.columns else "N/A",
        }
        
        # Top categories by median salary - handle case where job_category column might not exist
        top_categories = []
        if 'job_category' in self.df.columns:
            salary_stats = self.df.groupby('job_category').agg({
                'min_salary': ['median', 'mean', 'min', 'max', 'count'],
                'max_salary': ['median', 'mean'],
                'avg_salary': ['median', 'mean']
            }).sort_values(('avg_salary', 'median'), ascending=False)
            
            for i, category in enumerate(salary_stats.head(5).index, 1):
                median = salary_stats.loc[category, ('avg_salary', 'median')]
                count = salary_stats.loc[category, ('min_salary', 'count')]
                top_categories.append({
                    'name': category,
                    'median_salary': f"{median:.0f}",
                    'count': int(count)
                })
        else:
            # Add placeholder if job_category doesn't exist
            print("Warning: 'job_category' column not found. Using placeholder values.")
            top_categories = [{'name': 'Data not available', 'median_salary': 'N/A', 'count': 0}]
        
        # Seniority level data - handle case where seniority column might not exist or be empty
        seniority_levels = []
        if 'seniority' in self.df.columns and not self.df['seniority'].empty:
            # Filter out rows where seniority is NaN or empty string
            df_seniority = self.df[self.df['seniority'].notna() & (self.df['seniority'] != '')]
            
            if not df_seniority.empty:
                seniority_stats = df_seniority.groupby('seniority').agg({
                    'avg_salary': ['median', 'mean', 'min', 'max', 'count']
                }).sort_values(('avg_salary', 'median'))
                
                for level in ['Junior', 'Mid', 'Senior']:
                    if level in seniority_stats.index:
                        median = seniority_stats.loc[level, ('avg_salary', 'median')]
                        count = seniority_stats.loc[level, ('avg_salary', 'count')]
                        seniority_levels.append({
                            'name': level,
                            'median_salary': f"{median:.0f}",
                            'count': int(count)
                        })
        
        # If seniority data is empty, add placeholder
        if not seniority_levels:
            print("Warning: No valid 'seniority' data found. Using placeholder values.")
            seniority_levels = [
                {'name': 'Junior', 'median_salary': 'N/A', 'count': 0},
                {'name': 'Mid', 'median_salary': 'N/A', 'count': 0},
                {'name': 'Senior', 'median_salary': 'N/A', 'count': 0}
            ]
        
        # Find the most in-demand role (highest count) - use 'Title' column instead of 'job_title'
        role_counts = self.df['Title'].value_counts() if 'Title' in self.df.columns else pd.Series()
        most_demand_role = role_counts.index[0] if not role_counts.empty else "Data not available"
        
        # Find most common company - use 'Company' instead of 'company'
        company_counts = self.df['Company'].value_counts() if 'Company' in self.df.columns else pd.Series()
        top_hiring_company = company_counts.index[0] if not company_counts.empty else "Data not available"
        
        # No tech stack column available in the provided CSV structure
        tech_stack = "Data not available"
        
        # Calculate a notable market move based on available data
        notable_market_move = "Data not available"
        if 'seniority' in self.df.columns and not self.df['seniority'].empty:
            senior_avg = self.df[self.df['seniority'] == 'Senior']['avg_salary'].mean() if 'Senior' in self.df['seniority'].values else 0
            if senior_avg > 0:
                notable_market_move = f"Senior positions average salary: €{senior_avg:.0f}"
        
        # Get top roles without YoY change since we don't have historical data
        top_roles = []
        for i, (role, count) in enumerate(role_counts.head(5).items(), 1):
            role_data = self.df[self.df['Title'] == role]
            median_salary = role_data['avg_salary'].median() if not role_data.empty else 0
            top_roles.append({
                'name': role,
                'median_salary': f"{median_salary:.0f}" if median_salary > 0 else "N/A",
                'yoy_change': "N/A"  # We don't have historical data for YoY comparison
            })
        
        # Get highlights either from custom highlights or from data
        highlights = self.get_highlights_from_data()
        
        # Use custom highlights if provided
        if hasattr(self, 'custom_highlights'):
            for key, value in self.custom_highlights.items():
                highlights[key] = value
        
        newsletter_data = {
            'newsletter_title': 'Weekly IT Salary Market Insights',
            'newsletter_date': datetime.now().strftime('%B %d, %Y'),
            'overall_min_salary': overall_stats['min_salary'],
            'overall_max_salary': overall_stats['max_salary'],
            'overall_avg_salary': overall_stats['avg_salary'],
            'overall_median_salary': overall_stats['median_salary'],
            'top_categories': top_categories,
            'seniority_levels': seniority_levels,
            'visualizations': visualizations,
            'most_demand_role': highlights.get('most_demand_role', 'Data not available'),
            'top_hiring_company': highlights.get('top_hiring_company', 'Data not available'),
            'most_demand_tech': highlights.get('most_demand_tech', 'Data not available'),
            'notable_market_move': highlights.get('notable_market_move', 'Data not available'),
            'top_roles': top_roles,
            'include_trends': True,
            'trends_content': "Analysis based only on current data. Historical trends not available.",
            'include_hot_positions': True,
            'hot_positions_content': "Based on position frequency in our dataset."
        }
        
        return newsletter_data
    
    def generate_html_newsletter(self, template_name='simple_template.html', output_name=None):
        """Generate HTML newsletter from template and data"""
        if self.df is None:
            print("No data loaded. Please call load_data() first.")
            return None
        
        # Prepare newsletter data
        newsletter_data = self.prepare_newsletter_data()
        
        # Load template
        template_path = os.path.join(self.template_dir, template_name)
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Render template with Jinja2
        template = jinja2.Template(template_content)
        rendered_html = template.render(**newsletter_data)
        
        # Save HTML file
        if output_name is None:
            output_name = f"newsletter_{datetime.now().strftime('%Y%m%d')}.html"
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, 'w') as f:
            f.write(rendered_html)
        
        print(f"Newsletter HTML saved to {output_path}")
        return output_path, rendered_html, newsletter_data
    
    def send_newsletter_email(self, recipients, subject=None, sender_email=None, 
                            sender_password=None, smtp_server='smtp.gmail.com', 
                            smtp_port=587):
        """Send the newsletter via email"""
        if sender_email is None or sender_password is None:
            print("Error: Email credentials required. Please provide sender_email and sender_password.")
            return False
        
        # Generate newsletter
        _, html_content, newsletter_data = self.generate_html_newsletter()
        
        if subject is None:
            subject = newsletter_data['newsletter_title']
        
        # Create message
        message = MIMEMultipart('related')
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
        
        # Create the HTML part
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)
        
        # Attach images with proper Content-ID references
        for img_id, img_data in newsletter_data['visualizations'].items():
            with open(img_data['path'], 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', f'<{img_id}>')
                img.add_header('Content-Disposition', 'inline', filename=f"{img_id}.png")
                message.attach(img)
        
        # Attach the company logo
        try:
            logo_path = 'images/Company_logo.png'  # Path to your logo image
            with open(logo_path, 'rb') as logo_file:
                logo_img = MIMEImage(logo_file.read())
                logo_img.add_header('Content-ID', '<company_logo>')
                logo_img.add_header('Content-Disposition', 'inline', filename="Company_logo.png")
                message.attach(logo_img)
        except FileNotFoundError:
            print(f"Warning: Logo file not found at {logo_path}. Continuing without logo.")
        except Exception as e:
            print(f"Warning: Could not attach logo: {e}. Continuing without logo.")
        
        # Attach the highlight images
        highlight_images = [
            {'path': 'images/Binocular--Streamline-Ultimate.png', 'cid': 'binocular'},
            {'path': 'images/Iris-Scan-1--Streamline-Ultimate.png', 'cid': 'iris_scan'},
            {'path': 'images/Splitting.png', 'cid': 'splitting'}
        ]
        
        for img_info in highlight_images:
            try:
                with open(img_info['path'], 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', f'<{img_info["cid"]}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_info['path']))
                    message.attach(img)
            except FileNotFoundError:
                print(f"Warning: Image file not found at {img_info['path']}. Continuing without image.")
            except Exception as e:
                print(f"Warning: Could not attach image: {e}. Continuing without image.")
        
        try:
            # Connect to server and send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
            print(f"Newsletter sent successfully to {recipients}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def add_trend_data(self, trends_content):
        """Add industry trends data for the next newsletter"""
        # This would be expanded in the future to handle complex trend data
        self.trends_content = trends_content
        self.include_trends = True
    
    def add_hot_positions(self, positions_data):
        """Add hot positions data for the next newsletter"""
        # This would be expanded in the future to handle position data
        self.hot_positions_content = positions_data
        self.include_hot_positions = True

    def add_custom_highlights(self, most_demand_role=None, top_hiring_company=None, 
                             most_demand_tech=None, notable_market_move=None):
        """Add custom highlight data for the key highlights section"""
        if not hasattr(self, 'custom_highlights'):
            self.custom_highlights = {}
        
        if most_demand_role:
            self.custom_highlights['most_demand_role'] = most_demand_role
        
        if top_hiring_company:
            self.custom_highlights['top_hiring_company'] = top_hiring_company
            
        if most_demand_tech:
            self.custom_highlights['most_demand_tech'] = most_demand_tech
            
        if notable_market_move:
            self.custom_highlights['notable_market_move'] = notable_market_move
            
    def get_highlights_from_data(self):
        """Extract highlight data directly from the dataset"""
        highlights = {}
        
        # Most in-demand role (by count)
        if 'Title' in self.df.columns:
            role_counts = self.df['Title'].value_counts()
            if not role_counts.empty:
                highlights['most_demand_role'] = role_counts.index[0]
            else:
                highlights['most_demand_role'] = "Data not available"
        else:
            highlights['most_demand_role'] = "Data not available"
        
        # Top hiring company
        if 'Company' in self.df.columns:
            company_counts = self.df['Company'].value_counts()
            if not company_counts.empty:
                highlights['top_hiring_company'] = company_counts.index[0]
            else:
                highlights['top_hiring_company'] = "Data not available"
        else:
            highlights['top_hiring_company'] = "Data not available"
        
        # We don't have tech stack data
        highlights['most_demand_tech'] = "Data not available"
        
        # Notable market move - find highest paying job category
        if 'job_category' in self.df.columns and 'avg_salary' in self.df.columns:
            category_salaries = self.df.groupby('job_category')['avg_salary'].median().sort_values(ascending=False)
            if not category_salaries.empty:
                top_category = category_salaries.index[0]
                top_salary = category_salaries.iloc[0]
                highlights['notable_market_move'] = f"Highest paying category: {top_category} (€{top_salary:.0f})"
            else:
                highlights['notable_market_move'] = "Data not available"
        else:
            highlights['notable_market_move'] = "Data not available"
        
        return highlights

# Example usage
def run_newsletter_generator():
    # Initialize the newsletter generator
    newsletter = SalaryNewsletter(data_file='processed_mega_dataset.csv')
    
    # Load the salary data
    if newsletter.load_data():
        # Generate the newsletter HTML using only data from the CSV
        output_path, _, _ = newsletter.generate_html_newsletter()
        print(f"Newsletter generated and saved to {output_path}")
        
        # To send via email (uncomment and provide credentials)
        newsletter.send_newsletter_email(
            # recipients=['ba.botinator@gmail.com', 'a.okuneviciute@ba.lt', 'dovran.eymirov@ktu.edu', 'mariia.prantsypal@ktu.edu', 'r.osipovice@ba.lt', 'martynuxgarlauskiux@gmail.com', 'sauleatene@protonmail.com'],
            recipients=['ba.botinator@gmail.com'],
            sender_email='ba.botinator@gmail.com',
            sender_password='mfdg jclg ngox rgql', 
            subject='Weekly IT Salary Market Newsletter'
        )

if __name__ == "__main__":
    run_newsletter_generator()