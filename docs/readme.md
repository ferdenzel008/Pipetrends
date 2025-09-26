# Pipetrends

An automated tool for daily extraction of most popular Youtube video and Google trends using Python. 

## Table of Contents
- [Introduction](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#introduction)
- [System Architecture](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#system-architecture)
- [Data Sources](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#data-sources)
- [ETL Workflow](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#etl-workflow)
- [Configuration](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#configuration)
- [How to Run](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#how-to-run)
- [Database Design](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#database-design)
- [Visualization Layer](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#visualization-layer)
- [Limitations & Future Improvements](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#limitations--future-improvements)
- [Contributing](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#contributing)
- [References](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#references)


## Introduction

Pipetrends is a data pipeline project that collects and processes trending information from two major sources:
- YouTube Data API → to retrieve trending videos and related analytical data.
- Google Trends (via Selenium web scraping) → to capture real-time search trends along with the search volume for each search trends.

</br>

The project is built with Python and follows a complete ETL (Extract, Transform, Load) workflow:
1. Extract raw data from APIs and web scraping.
2. Transform the data by cleaning, normalizing, and structuring it into analytics-ready tables.
3. Load the processed data into a PostgreSQL database for long-term storage and downstream analysis.
</br>
Additionally, the pipeline generates a log file that records key events and statuses during each run. This ensures better monitoring, debugging, and reproducibility of the data workflow.
</br>
</br>

By consolidating YouTube trends and Google search insights into a single storage layer, this project enables easier reporting, analysis, and dashboarding (e.g., with Power BI or other BI tools).

## System Architecture

### Project Architecture Diagram:

</br>

![Project Architecture Diagram](https://github.com/ferdenzel008/Pipetrends/blob/main/images/Project%20Architecture.jpg)

</br>

### Data Sources

### ETL logic (extract, transform, load)

### Storage layer (e.g., PostgreSQL, Smartsheet)

### Visualization

## Data Sources

Explain each source:

YouTube Data API (which endpoints, e.g., trending videos, video stats)

Google Trends (which parameters, e.g., region=PH, timeframe=24h)

Mention any limits or quotas.

## ETL Workflow

Step-by-step explanation of your pipeline:

Extract – Fetch raw data via APIs.

Transform – Cleaning, handling duplicates, normalizing timestamps, aggregating trends.

Load – Store results in database tables.

Show sample schemas (tables, columns).

## Configuration

Explain your .env file or config files.

Note on keeping credentials secure (gitignore).

## How to Run

Quick start command to run ETL.

Optional: scheduling (e.g., cron job, Airflow, Mage, etc. if you extend it).

## Database Design

Show ER diagram or schema structure.

Example:

videos table (video_id, title, channel, published_at…)

trends table (keyword, score, date…)

video_stats table (video_id, views, likes, comments, recorded_at)

## Visualization Layer

How to connect Power BI (or other BI tools).

Example queries / charts you built (screenshots are great here).

## Limitations & Future Improvements

Current limitations (e.g., API quotas, only PH region).

Possible extensions:

Add more countries.

Automate scheduling.

Use cloud storage (BigQuery, S3).

## Contributing

How others can add features / issues.

## References

Links to APIs used:

YouTube Data API

Google Trends PyTrends
