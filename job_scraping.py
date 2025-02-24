#!/usr/bin/env python3
import pandas as pd
import csv
import re
from datetime import datetime
from jobspy import scrape_jobs

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
    if any(keyword in loc.lower() for keyword in ["usa", "united states"]):
        return True
    # Check for pattern: "City, ST"
    match = re.search(r",\s*([A-Z]{2})$", loc)
    if match:
        state = match.group(1)
        if state in US_STATE_ABBREVS:
            return True
    return False

def compute_composite_score(row):
    """
    Compute a composite score based on available salary information and a bonus if
    the job description mentions 'benefits'. Note: The JobSpy schema does not include
    company recognition, so that part is omitted.
    """
    # Retrieve salary values (these fields come from the job_function portion of the schema)
    min_amount = row.get('min_amount')
    max_amount = row.get('max_amount')
    salary = 0
    if pd.notnull(min_amount) and pd.notnull(max_amount):
        salary = (min_amount + max_amount) / 2
    elif pd.notnull(min_amount):
        salary = min_amount
    elif pd.notnull(max_amount):
        salary = max_amount

    # Check for the keyword "benefits" in the description and add a bonus if present
    description = str(row.get('description', "")).lower()
    bonus = 5000 if "benefits" in description else 0
    remote = 50000 if row.get('is_remote') else 0

    return salary + bonus + remote

def main():
    print("Scraping remote backend/fullstack software engineering jobs for US residents...")

    # Scrape jobs from multiple boards using the python-jobspy library.
    # The search_term combines both "backend software engineer" and "fullstack software engineer".
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt"],
        search_term='("backend" OR "software engineer" OR "fullstack" OR "software" OR "engineer")',
        location="USA",              # Use "USA" to filter for US-based job postings where applicable
        results_wanted=500,           # Number of jobs to retrieve from each site
        hours_old=168,                # Only jobs posted in the last 72 hours
        is_remote=True,              # Filter for remote positions
        country_indeed='USA'         # Ensures Indeed & Glassdoor return US jobs
    )

    if jobs.empty:
        print("No jobs found matching the criteria.")
        return
    
    # Filter out roles whose TITLE doesn't contain "software" or "engineer"
    jobs = jobs[jobs["title"].str.contains("software|engineer|sde|backend|fullstack", case=False, na=False)]
    if jobs.empty:
        print("No software engineering jobs found after filtering.")
        return
    
    # Filter out roles where 'is_remote' is populated and equals False
    if 'is_remote' in jobs.columns:
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

    # Convert the 'date_posted' column to datetime (if available) so we can sort by recency.
    if 'date_posted' in jobs.columns:
        jobs['date_posted'] = pd.to_datetime(jobs['date_posted'], errors='coerce')

    # Compute the composite score for each job.
    jobs['composite_score'] = jobs.apply(compute_composite_score, axis=1)

    # Sort jobs by most recent posting (date_posted) and then by composite score.
    if 'date_posted' in jobs.columns:
        jobs_sorted = jobs.sort_values(by=['date_posted', 'composite_score'], ascending=[False, False])
    else:
        jobs_sorted = jobs.sort_values(by='composite_score', ascending=False)

    print(f"Found {len(jobs_sorted)} jobs.")
    print(jobs_sorted.head())

    # Drop the DESCRIPTION column before writing to file
    if 'description' in jobs_sorted.columns:
        jobs_sorted = jobs_sorted.drop(columns=['description'])

    # Create a unique filename using the current date and time as a prefix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_jobs_sorted.csv"

    # Export the sorted results to a CSV file.
    jobs_sorted.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"Results saved to {filename}.")

if __name__ == '__main__':
    main()
