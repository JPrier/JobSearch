# JobSpy Job Scraper

This project uses the [python-jobspy](https://github.com/cullenwatson/JobSpy) library to scrape and aggregate job postings from multiple job boards such as Indeed, LinkedIn, ZipRecruiter, Glassdoor, Google, and Bayt. The script is tailored to retrieve remote software engineering positions relevant to US residents. It includes customizable filtering and scoring mechanisms that allow you to fine-tune the results based on job titles, description keywords, and more.

## Features

- **Multi-Board Scraping:** Aggregates job postings from popular job boards concurrently.
- **Customizable Filters:**
  - **Title Filters:**  
    - **Inclusions:** Only include jobs whose titles contain key phrases (e.g., "software", "engineer", "backend", "fullstack").
    - **Exclusions:** Automatically filter out roles with irrelevant keywords (e.g., "principal" or "intern").
  - **Location Filters:** Ensures that only jobs with a valid US-based location are included. This check accepts explicit mentions (e.g., "USA", "United States") or city/state formats (e.g., "Boston, MA").
  - **Remote Jobs Only:** Filters out jobs that are not remote.
- **Composite Scoring:**  
  Calculates a composite score for each job using:
  - Salary (average of the minimum and maximum values, if available)
  - A **benefits bonus** if the description mentions "benefits"
  - **Keyword bonuses** from a configurable mapping (e.g., adding 1000 points for "backend")
  - A **remote bonus** if the job is marked as remote
- **Configurable Parameters:**  
  All key inputs such as search terms, timeframes, title filters, and scoring rules are stored in `config.py` for easy customization.
- **Output File:**  
  Saves results to a uniquely timestamped CSV file to prevent overwriting previous outputs.

## Files

- **main.py:**  
  The main script that performs scraping, filtering, scoring, and outputs the job data.
  
- **config.py:**  
  Contains all user-editable parameters (e.g., search terms, filter regexes, bonus mappings, and timeframes).
  
- **README.md:**  
  This file, which provides detailed documentation about the project.

## Prerequisites

- **Python 3.10 or later**
- Install required packages by running:

```bash
pip install -U python-jobspy pandas
```

## Usage

1. **Customize Configuration (Optional):**  
   Open `config.py` to adjust the following as needed:
   - **Job Boards & Search Terms:**  
     - `SITE_NAMES`: List of job boards.
     - `SEARCH_TERM`: The search term string for scraping jobs.
   - **Location & Time Filters:**  
     - `LOCATION`: The location filter (e.g., "USA").
     - `RESULTS_WANTED`: Number of results to retrieve per site.
     - `HOURS_OLD`: Only include jobs posted within the specified number of hours.
     - `IS_REMOTE`: Set to `True` to filter for remote positions.
   - **Title Filters:**  
     - `TITLE_INCLUSION_REGEX`: Regex pattern for required keywords in job titles.
     - `TITLE_EXCLUSION_REGEX`: Regex pattern for keywords to exclude from job titles.
   - **Scoring Bonuses:**  
     - `KEYWORD_SCORE_MAP`: Map of description keywords to bonus scores.
     - `REMOTE_BONUS`: Additional bonus value for jobs marked as remote.
   - **Output Cleanup:**  
     - `DROP_COLUMNS`: List of DataFrame columns to drop before saving the CSV.

2. **Run the Script:**  
   Execute the script from your terminal:

```bash
python job_scraping.py
```

3. **Review the Output:**  
   The script will produce a timestamped CSV file (e.g., `20250304_153045_jobs_sorted.csv`) containing the filtered and scored job listings.

## How It Works

1. **Scraping Jobs:**  
   The script uses the `scrape_jobs()` function from the python-jobspy library with parameters specified in `config.py` to fetch jobs across multiple boards.

2. **Filtering:**
   - **Title Filtering:**  
     - First, only jobs with titles that match the inclusion regex are retained.
     - Then, jobs with titles containing any of the exclusion keywords (like "principal" or "intern") are removed.
   - **Remote & Location Filtering:**  
     - Jobs are further filtered to include only those that are remote (if applicable) and have a valid US location.
     
3. **Composite Scoring:**  
   For each job, a composite score is calculated by:
   - Averaging available salary data.
   - Scanning the job description for keywords defined in `KEYWORD_SCORE_MAP` and adding the corresponding bonus.
   - Adding a remote bonus if the job is remote.

4. **Sorting & Output:**  
   Jobs are sorted by the most recent posting date and their composite score. Unnecessary columns are dropped, and the final results are saved to a uniquely named CSV file.

