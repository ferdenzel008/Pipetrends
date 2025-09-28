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

- Youtube

  For this project, YouTube serves as a primary source of trending video content. Since the pipeline is designed to highlight what’s relevant to a local audience, we focus specifically on the Philippines (PH) region. By     doing this, we capture the most popular and relevant videos trending within that geographic area.

  - Endpoint used: videos.list() from the YouTube Data API.

  - Parameters included:

    - snippet → to capture video metadata such as title, channel, description, and publish time.

    - statistics → to track key engagement metrics like view count, like count, and comment count.

    - contentDetails → to obtain information such as duration and definition (HD/SD).

  - Results per request: We limit API calls to 25 videos per request, which aligns with YouTube’s default maximum result size for this endpoint.

  This approach ensures that the pipeline efficiently captures trending video data while respecting API quota limits and focusing only on the most impactful videos in the PH region.
  
- Google Trends

  In addition to YouTube, this project also sources from Google Trends to capture data that the people are actively searching for in the Philippines. Since the Google Trends website provides insights only through its        front-end interface, we implemented web scraping with Selenium to collect the trending queries.

  - Query Limitations:

    - The Google Trends table displays only 25 search queries at a time.

    - Accessing queries beyond the top 25 requires clicking “Next” in the UI, which complicates scraping.

    - Since Selenium is our current web scraping tool, we limit collection to the top 25 results per run.

  - Sorting & Filtering:

    - We apply a sort filter (highest → lowest search volume) so the pipeline captures the top trending queries used in the region.

  - Timeframe:

    - Data is collected for the last 24 hours.

    - This aligns with the pipeline’s design to run once daily, ensuring that we always capture the most recent and relevant trends.

  This setup provides a practical balance between data availability and implementation complexity, focusing on the top 25 most significant search queries in the PH region each day. 

### ETL logic (extract, transform, load)
  
  - Extraction
    
    
    - Youtube

      Prerequisites:
      - Google account (For Google Console)
      - Youtube API key
    
      </br>
      
      First we initialize the API client:
       ```python
       youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
       ```
       
       </br>
       
      Using the videos.list method on the Youtube Data API, we can extract the trending videos and their respective data. The list can be filtered by region and limit the number of results in the list. For more info you can check the videos.list method on Youtube Data        API's documentation (https://developers.google.com/youtube/v3/docs/videos/list)
      ```python
      request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=min(max_results, 25)
        )
      ```
        - snippet: This object contains the title, description, publishedAt, channelId, channelTitle, thumbnails, categoryId, liveBroadcastContent, and localized variables for the video.
        - statistics: This object contains viewCount, likeCount, favoriteCount, commentCount variables for the video.
      
      </br>

      fasdfq  
    - Google Trends

### Storage layer (e.g., PostgreSQL, Smartsheet)

### Visualization

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
