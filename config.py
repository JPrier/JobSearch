# config.py
# User-configurable parameters for the JobSpy Job Scraper

# List of job boards to scrape
SITE_NAMES = ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt"]

# Search term for scraping jobs.
SEARCH_TERM = '("backend" OR "software engineer" OR "fullstack" OR "software" OR "engineer")'

# Location filter
LOCATION = "USA"

# Number of job results to retrieve per site
RESULTS_WANTED = 10000

# Only include jobs posted within the last X hours (e.g., 168 hours = 7 days)
HOURS_OLD = 336

# Filter for remote positions
IS_REMOTE = True

# Country parameter for Indeed and Glassdoor searches
COUNTRY_INDEED = 'USA'

# Title filtering parameters
# Titles must include at least one of these keywords (case-insensitive)
TITLE_INCLUSION_REGEX = "software|engineer|sde|backend|fullstack|developer"
# Titles with these keywords will be excluded (case-insensitive)
TITLE_EXCLUSION_REGEX = "principal|intern|staff|director|distinguished|executive|manager|entry|junior|chief|support|qa|electrical|geotechnical"

# Mapping of keywords to bonus scores to be added when found in the job description (case-insensitive)
KEYWORD_SCORE_MAP = {
    "backend": 10000,
    "fullstack": 500,
    "frontend": -200,
    "microservices": 500,
    "distributed": 500,
    "cloud": 700,
    "aws": 10000,
    "benefits": 500,
    "python": 1000,
    "java": 10000,
}

# Additional bonus scores
REMOTE_BONUS = 50000

# List of columns to drop before writing to the output file
DROP_COLUMNS = [
    'description',
    'job_url_direct',
    "company_logo",
    "company_url_direct",
    "company_addresses",
    "company_num_employees",
    "company_revenue",
    "company_description",
    "salary_source",
    "interval",
    "job_level",
    "job_function",
    "is_remote",
    "company_industry",
    "job_type",
    "listing_type",

]
