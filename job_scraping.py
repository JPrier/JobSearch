#!/usr/bin/env python3
import pandas as pd
import csv
import re
from datetime import datetime
from jobspy import scrape_jobs
import config

# Set of valid US state abbreviations (including DC)
US_STATE_ABBREVS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", 
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", 
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", 
    "WI", "WY", "DC"
}

def is_us_location(location):
    """
    Returns True if the location string indicates a US-based location.
    Accepts explicit terms ("USA", "United States") or a pattern like "City, ST"
    where ST is a valid US state abbreviation.
    """
    if pd.isnull(location):
        return True
    loc = location.strip()
    # Check if location explicitly contains US-related keywords.
    if any(keyword in loc.lower() for keyword in ["remote", "us", "usa", "united states"]):
        return True
    # Check for pattern: "City, ST"
    match = re.search(r",\s*([A-Z]{2})$", loc)
    if not match:
        return False
    state = match.group(1)
    if state in US_STATE_ABBREVS:
        return True
    return False

def compute_composite_score(row):
    """
    Compute a composite score based on available salary information,
    bonuses for keywords found in the job description, benefits bonus,
    and a remote bonus.
    """
    # Retrieve salary values (from the job_function portion of the schema)
    min_amount = row.get('min_amount')
    max_amount = row.get('max_amount')
    salary = 0
    if pd.notnull(min_amount) and pd.notnull(max_amount):
        salary = (min_amount + max_amount) / 2
    elif pd.notnull(min_amount):
        salary = min_amount
    elif pd.notnull(max_amount):
        salary = max_amount

    # Convert description to lowercase string for analysis.
    description = str(row.get('description', "")).lower()

    # Keyword bonus from config.KEYWORD_SCORE_MAP
    keyword_bonus = 0
    for keyword, bonus in config.KEYWORD_SCORE_MAP.items():
        if keyword.lower() in description:
            keyword_bonus += bonus

    # Remote bonus
    remote_bonus = config.REMOTE_BONUS if config.IS_REMOTE and row.get('is_remote') else 0

    return salary + keyword_bonus + remote_bonus

def main():
    print("Scraping remote backend/fullstack software engineering jobs for US residents...")

    # Scrape jobs from multiple boards using the python-jobspy library.
    jobs = scrape_jobs(
        site_name=config.SITE_NAMES,
        search_term=config.SEARCH_TERM,
        location=config.LOCATION,
        results_wanted=config.RESULTS_WANTED,
        hours_old=config.HOURS_OLD,
        is_remote=config.IS_REMOTE,
        country_indeed=config.COUNTRY_INDEED
    )

    if jobs.empty:
        print("No jobs found matching the criteria.")
        return
    
    # Filter in only jobs whose title matches inclusion keywords
    jobs = jobs[jobs["title"].str.contains(config.TITLE_INCLUSION_REGEX, case=False, na=False)]
    # Filter out job titles with irrelevant keywords (like "principal" or "intern")
    jobs = jobs[~jobs["title"].str.contains(config.TITLE_EXCLUSION_REGEX, case=False, na=False)]
    
    if jobs.empty:
        print("No software engineering jobs found after filtering by title.")
        return
    
    # Filter out roles where 'is_remote' is populated and equals False.
    if config.IS_REMOTE and 'is_remote' in jobs.columns:
        jobs = jobs[jobs["is_remote"].isnull() | (jobs["is_remote"] == True)]
        if jobs.empty:
            print("No remote jobs found after filtering by is_remote flag.")
            return

    # Filter out rows that do not have a valid US location.
    if 'location' in jobs.columns:
        jobs = jobs[jobs["location"].apply(is_us_location)]
        if jobs.empty:
            print("No jobs found with a valid US location after filtering by location.")
            return

    # Filter out jobs that are not fulltime. Only keep jobs with a job_type of "fulltime" (or null).
    if 'job_type' in jobs.columns:
        jobs = jobs[(jobs['job_type'].isnull()) | (jobs['job_type'].str.lower().isin(['fulltime', 'full-time']))]
        if jobs.empty:
            print("No fulltime jobs found after filtering by job_type.")
            return

    # Filter out jobs that are hourly. Only keep jobs with an interval other than "hourly" (or null).
    if 'interval' in jobs.columns:
        jobs = jobs[(jobs['interval'].isnull()) | (jobs['interval'].str.lower() != 'hourly')]
        if jobs.empty:
            print("No salary jobs found after filtering out hourly positions.")
            return

    # Convert the 'date_posted' column to datetime (if available) so we can sort by recency.
    if 'date_posted' in jobs.columns:
        jobs['date_posted'] = pd.to_datetime(jobs['date_posted'], errors='coerce')

    # Compute the composite score for each job.
    jobs['composite_score'] = jobs.apply(compute_composite_score, axis=1)

    # Sort jobs by most recent posting (date_posted) and then by composite score.
    if 'date_posted' in jobs.columns:
        jobs_sorted = jobs.sort_values(by=['composite_score','date_posted'], ascending=[False, False])
    else:
        jobs_sorted = jobs.sort_values(by='composite_score', ascending=False)

    print(f"Found {len(jobs_sorted)} jobs.")

    # Drop unnecessary columns before writing to file.
    jobs_sorted = jobs_sorted.drop(columns=config.DROP_COLUMNS, errors='ignore')
    print(jobs_sorted.head())

    # Create a unique filename using the current date and time as a prefix.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_jobs_sorted.csv"

    # Export the sorted results to a CSV file.
    jobs_sorted.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Results saved to {filename}.")

if __name__ == '__main__':
    main()

