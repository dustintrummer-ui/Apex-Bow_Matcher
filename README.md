# Apex Bow Matcher

A mobile-friendly compound bow matching tool that helps users find bows with similar ATA length, brace height, draw length, and draw weight compatibility.

## Project Goal

Archers can select a bow they currently shoot and receive similar bow recommendations based on measurable specifications.

## Tech Stack

- Python
- BeautifulSoup
- Pandas
- SQLite
- Streamlit

## ETL Pipeline

1. Extract: scrape bow data from Compound Bow Choice
2. Transform: clean and normalize bow specs
3. Load: store cleaned data in SQLite

## App Features

- Brand → model → year dropdown filtering
- User-selected ATA and brace tolerance
- Minimum year filter
- Match scoring system
- Top 10 similar bows
- Displays selected bow specs

## Project Files

- `bowscraper.py` - scrapes raw bow data
- `bowprocessor.py` - cleans scraped data
- `bowdatabase.py` - loads data into SQLite
- `bowmatch.py` - matching/scoring engine
- `bow_app.py` - Streamlit UI

## How to Run

```bash
python -m streamlit run bow_app.pyt.
