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

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as path_effects
from matplotlib.patches import Rectangle, PathPatch
from matplotlib.path import Path
import numpy as np
import os
import matplotlib as mpl
from io import BytesIO

def download_inter_font():
    """Download and install the Inter font if it's not already available"""
    import os
    import urllib.request
    import zipfile
    from io import BytesIO
    
    # Create fonts directory if it doesn't exist
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # Path to save the Inter font
    font_path = os.path.join(fonts_dir, 'Inter-Regular.ttf')
    
    # Check if font already exists
    if os.path.isfile(font_path):
        print("Inter font already exists at:", font_path)
        return font_path
    
    try:
        # URL for the Inter font
        url = 'https://github.com/rsms/inter/releases/download/v3.19/Inter-3.19.zip'
        print("Downloading Inter font from GitHub...")
        
        # Download the zip file
        response = urllib.request.urlopen(url)
        zip_data = BytesIO(response.read())
        
        # Extract the font file from the zip
        with zipfile.ZipFile(zip_data) as font_zip:
            # Find the Regular font file in the zip
            for file_info in font_zip.infolist():
                if file_info.filename.endswith('Inter-Regular.ttf'):
                    # Extract the font to our fonts directory
                    font_zip.extract(file_info, fonts_dir)
                    # Move it to the right location if necessary
                    extracted_path = os.path.join(fonts_dir, file_info.filename)
                    if extracted_path != font_path:
                        import shutil
                        os.makedirs(os.path.dirname(font_path), exist_ok=True)
                        shutil.move(extracted_path, font_path)
                    break
        
        print("Successfully downloaded and installed Inter font to:", font_path)
        return font_path
    
    except Exception as e:
        print(f"Error downloading Inter font: {e}")
        return None

class SalaryNewsletter:


    def __init__(self, data_file='processed_mega_dataset.csv'):
        """Initialize the newsletter generator with data file path"""
        self.data_file = data_file
        self.df = None
        self.template_dir = 'newsletter_templates'
        self.output_dir = 'newsletter_output'
        self.image_dir = 'newsletter_images'

                    # Set up font
        self.setup_font()
        
        # Create necessary directories
        for directory in [self.template_dir, self.output_dir, self.image_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Create or update default template
        template_updated = self._create_default_template()
        if template_updated:
            print("Template was created or updated to match the current code definition.")

    def setup_font(self):
        try:
            # First try to download the font if it's not already available
            font_path = download_inter_font()
            
            if font_path and os.path.isfile(font_path):
                # If we have the font file, register it with matplotlib
                fm.fontManager.addfont(font_path)
                mpl.rcParams['font.family'] = 'Inter'
                print("Using Inter font from:", font_path)
                return
            
            # Check if Inter is already in the font list
            font_names = [f.name for f in fm.fontManager.ttflist]
            if 'Inter' in font_names:
                mpl.rcParams['font.family'] = 'Inter'
                print("Using system-installed Inter font")
                return
            
            # If Inter is not found, fall back to a standard sans-serif font
            print("Inter font not found, using system sans-serif font instead")
            mpl.rcParams['font.family'] = 'sans-serif'
            
        except Exception as e:
            print(f"Error setting up font: {e}")
            # If anything goes wrong, use a safe fallback
            mpl.rcParams['font.family'] = 'sans-serif'
        
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
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 0;
            background-color: #f9f9f9;
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
            font-size: 14px;
            margin-bottom: 5px;
            font-weight: normal;
        }
        .title {
            color: #3b74d9;
            font-size: 24px;
            font-weight: bold;
            margin: 5px 0;
        }
        .subtitle {
            font-size: 16px;
            margin-top: 5px;
            margin-bottom: 15px;
        }
        .content {
            padding: 20px;
        }
        .highlights {
            background-color: #f0f6ff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .highlights-title {
            font-size: 18px;
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
        }
        .highlight-label {
            color: #3b74d9;
            font-weight: bold;
            margin-right: 5px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 22px;
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
            font-size: 12px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h3 class="welcome-text">Welcome back to  second version</h3>
            <h1 class="title">{{ newsletter_title }}</h1>
            <p class="subtitle">{{ newsletter_date }}</p>
            <p>Stay informed with the latest hiring trends, tech stacks, and salary insights across the Baltics.</p>
        </div>
        
        <div class="content">
            <div class="highlights">
                <h2 class="highlights-title">Key Highlights This Week</h2>
                
                <div class="highlight-item">
                    <div class="highlight-icon"></div>
                    <div class="highlight-text">
                        <span class="highlight-label">Most In-Demand Role:</span>
                        <span>{{ most_demand_role }}</span>
                    </div>
                </div>
                
                <div class="highlight-item">
                    <div class="highlight-icon"></div>
                    <div class="highlight-text">
                        <span class="highlight-label">Top Hiring Company:</span>
                        <span>{{ top_hiring_company }}</span>
                    </div>
                </div>
                
                <div class="highlight-item">
                    <div class="highlight-icon"></div>
                    <div class="highlight-text">
                        <span class="highlight-label">Most In-Demand Tech Stack:</span>
                        <span>{{ most_demand_tech }}</span>
                    </div>
                </div>
                
                <div class="highlight-item">
                    <div class="highlight-icon"></div>
                    <div class="highlight-text">
                        <span class="highlight-label">Notable Market Move:</span>
                        <span>{{ notable_market_move }}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">Trends This Month</h2>
                <h3 class="subsection-title">Top Roles In Demand</h3>
                
                <div class="chart">
                    <img src="cid:top_roles_chart" alt="Top Roles In Demand">
                </div>
                <p>The chart above shows the top roles in demand based on position frequency and median salary.</p>
            </div>
            
            <div class="section">
                <h2 class="section-title">Salary Distribution by Job Category</h2>
                <div class="chart">
                    <img src="cid:salary_distribution" alt="Salary Distribution by Job Category">
                </div>
                <p>The chart above shows the distribution of salaries across different job categories.</p>
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
            <p>This newsletter is generated automatically based on Baltic IT job market data.</p>
            <p>To unsubscribe, please reply with "UNSUBSCRIBE" in the subject line.</p>
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
        
        # Generate seniority level chart
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='seniority', y='avg_salary', data=self.df, 
                   order=['Junior', 'Mid', 'Senior'])
        plt.title('Salary Distribution by Seniority Level', fontsize=16)
        plt.xlabel('Seniority Level', fontsize=14)
        plt.ylabel('Average Salary (€)', fontsize=14)
        plt.tight_layout()
        
        # Save as image file and as bytes for email embedding
        salary_seniority_path = os.path.join(self.image_dir, 'salary_seniority.png')
        plt.savefig(salary_seniority_path)
        
        salary_seniority_buffer = BytesIO()
        plt.savefig(salary_seniority_buffer, format='png')
        salary_seniority_buffer.seek(0)
        plt.close()
        
        # NEW: Generate top roles chart
        plt.figure(figsize=(12, 8))
        
        # Get top 5 roles by count - use job_category instead of Title
        if 'job_category' in self.df.columns:
            role_counts = self.df['job_category'].value_counts().head(5)
            roles = role_counts.index.tolist()
            counts = role_counts.values
            
            # Create figure
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            
            # Create a light blue background with rounded corners
            # Define the rectangle with rounded corners
            height = max(counts) * 1.2
            width = len(roles) + 0.5
            
            # Create a custom rounded rectangle for background
            def rounded_rect(x, y, width, height, radius=0.3):
                # Create the points of the rounded rectangle
                xs = [x + radius, x + width - radius, x + width, x + width, x + width - radius, x + radius, x, x, x + radius]
                ys = [y, y, y + radius, y + height - radius, y + height, y + height, y + height - radius, y + radius, y]
                
                # Create the rectangle path
                codes = [Path.MOVETO] + [Path.LINETO] * 7 + [Path.CLOSEPOLY]
                path = Path(list(zip(xs, ys)), codes)
                return PathPatch(path, facecolor='#f0f6ff', alpha=0.5, edgecolor='none', zorder=0)
            
            # Add the rounded rectangle to the plot
            ax.add_patch(rounded_rect(-0.5, 0, width, height))
            
            # Create bars
            for i, count in enumerate(counts):
                # Create a rectangle for each bar
                bar = FancyBboxPatch(
                    (i - 0.35, 0),  # x, y (left corner)
                    width=0.7,      # width of the bar
                    height=count,   # height based on count
                    boxstyle="round,pad=0,rounding_size=0.7",  # rounded corners
                    facecolor='#2D7FF9',  # blue color
                    alpha=1.0,
                    zorder=2
                )
                ax.add_patch(bar)
            
            # Set up the axis
            ax.set_xlim(-0.5, len(roles) - 0.5)
            ax.set_ylim(0, max(counts) * 1.2)  # Add some space at the top
            ax.set_xticks(range(len(roles)))
            
            # Set x-tick labels to job category name + count
            ax.set_xticklabels([f"{role} ({count})" for role, count in zip(roles, counts)], rotation=0, fontname='Inter')
            
            # Remove the vertical y-axis label and place horizontally at the top
            ax.set_ylabel('')  # Remove the default y-axis label
            ax.text(-0.5, max(counts) * 1.1, 'Job Postings', fontsize=12, ha='left', fontname='Inter')
            
            # Remove spines/borders
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            
            # Remove title and values above bars
            # ax.set_title('Top Roles In Demand', fontsize=18)  # Title removed
            
            plt.tight_layout()
            
            # Save as image file and bytes for email embedding
            top_roles_path = os.path.join(self.image_dir, 'top_roles_chart.png')
            plt.savefig(top_roles_path)
            
            top_roles_buffer = BytesIO()
            plt.savefig(top_roles_buffer, format='png')
            top_roles_buffer.seek(0)
            plt.close()
        else:
            # Create placeholder chart if job_category column doesn't exist
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'Data not available', 
                    horizontalalignment='center', verticalalignment='center', fontsize=16, fontname='Inter')
            plt.axis('off')
            plt.tight_layout()
            
            top_roles_path = os.path.join(self.image_dir, 'top_roles_chart.png')
            plt.savefig(top_roles_path)
            
            top_roles_buffer = BytesIO()
            plt.savefig(top_roles_buffer, format='png')
            top_roles_buffer.seek(0)
            plt.close()

        return {
            'salary_distribution': {
                'path': salary_dist_path,
                'buffer': salary_dist_buffer
            },
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
        message = MIMEMultipart('alternative')  # Changed from 'related' to 'alternative'
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
        
        # Create the HTML part
        html_part = MIMEMultipart('related')  # Use 'related' for the HTML part with images
        html_part.attach(MIMEText(html_content, 'html'))
        
        # Attach the HTML part to the main message
        message.attach(html_part)
        
        # Attach images with proper Content-ID references
        for img_id, img_data in newsletter_data['visualizations'].items():
            with open(img_data['path'], 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', f'<{img_id}>')
                img.add_header('Content-Disposition', 'inline', filename=f"{img_id}.png")
                # Attach images to the related HTML part
                html_part.attach(img)
        
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
            recipients=['ba.botinator@gmail.com'],
            sender_email='ba.botinator@gmail.com',
            sender_password='mfdg jclg ngox rgql', 
            subject='Weekly IT Salary Market Newsletter'
        )

if __name__ == "__main__":
    run_newsletter_generator()