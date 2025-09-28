# Pipetrends

An automated tool for daily extraction of most popular Youtube video and Google trends using Python. 

## Table of Contents
- [Introduction](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#introduction)
- [System Architecture](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#system-architecture)
- [Data Sources](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#data-sources)
- [ETL Logic](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#etl-logic-extract-transform-load)
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

- **Youtube**
  ***
  For this project, YouTube serves as a primary source of trending video content. Since the pipeline is designed to highlight what’s relevant to a local audience, we focus specifically on the Philippines (PH) region. By     doing this, we capture the most popular and relevant videos trending within that geographic area.

  - Endpoint used: videos.list() from the YouTube Data API.

  - **Parameters included:**

    - snippet: to capture video metadata such as title, channel, description, and publish time.

    - statistics: to track key engagement metrics like view count, like count, and comment count.

  - Results per request: We limit API calls to 25 videos per request, which aligns with YouTube’s default maximum result size for this endpoint.

  This approach ensures that the pipeline efficiently captures trending video data while respecting API quota limits and focusing only on the most impactful videos in the PH region.

  ***
  
- **Google Trends**

  ***

  In addition to YouTube, this project also sources from Google Trends to capture data that the people are actively searching for in the Philippines. Since the Google Trends website provides insights only through its        front-end interface, we implemented web scraping with Selenium to collect the trending queries.

  - **Query Limitations:**

    - The Google Trends table displays only 25 search queries at a time.

    - Accessing queries beyond the top 25 requires clicking “Next” in the UI, which complicates scraping.

    - Since Selenium is our current web scraping tool, we limit collection to the top 25 results per run.

  - **Sorting & Filtering:**

    - We apply a sort filter (highest → lowest search volume) so the pipeline captures the top trending queries used in the region.

  - **Timeframe:**

    - Data is collected for the last 24 hours.

    - This aligns with the pipeline’s design to run once daily, ensuring that we always capture the most recent and relevant trends.

  This setup provides a practical balance between data availability and implementation complexity, focusing on the top 25 most significant search queries in the PH region each day. 

  ***
  
</br>
</br>

### ETL logic (extract, transform, load)
  
  - **Extraction**
  
    ***
  
    - **Youtube**

      **Prerequisites:**
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

      **Extracted Data Fields:**
      - Video ID
      - Snippet
        - title: The title of the video.
        - description: The description provided by the uploader.
        - publishedAt: The date and time the video was published.
        - channelId: The unique ID of the channel that uploaded the video.

      - Statistics
        - viewCount: The total number of views.
        - likeCount: The total number of likes.
        - commentCount: The total number of comments.
      
      </br>
      </br>
  
    - **Google Trends**

      **Prerequisites:**

      - Chrome browser
      - ChromeDriver (compatible with your Chrome version)

      </br>

      First, initialize the Selenium Chrome driver:

      ```python
      options = webdriver.ChromeOptions()
      options.add_argument("--headless")  # run without opening browser
      driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
      ```

      </br>

      Next, set the URL for scraping:
      ```python
      url = "https://trends.google.com/trending?geo=PH&hl=en-US&tz=360&sort=search-volume&hours=24"
      driver.get(url)
      time.sleep(10)
      ```
      - geo=PH: Filters the trends to the Philippines.
      - sort=search-volume: Ensures queries are sorted by highest search volume.
      - hours=24: Limits the data to only the last 24 hours of trends.

      </br>

      **Scraping Logic:**

      Using Selenium, we locate the div elements containing the search query and search volume. These can be identified through their CSS selectors.
      
      ```python
      trending_elements = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
      search_volume_elem = driver.find_elements(By.CSS_SELECTOR, "div.lqv0Cb")
      ```

      </br>

      **Extracted Data Fields:**

      - Search Query: The trending keyword or phrase.
      - Search Volume: The popularity measure
     
    ***

      </br>
      </br>
      
   
 
- **Transformation**
  
  ***
  
  - **Youtube**
    
    As far as the transformation of data is concerned, we ensured that the data types in our PostgreSQL tables matched the extracted data.

      - title, description, channelId: Saved as TEXT, no transformation required.
      - publishedAt: Already in ISO 8601 date-time format, no transformation required.
      - viewCount, likeCount, commentCount: Parsed from string to INT before saving.
    </br>    
    This guarantees that the extracted data is properly aligned with PostgreSQL’s schema requirements.

    </br>
    </br>

  - **Google Trends**

    For Google Trends, the transformation focused mainly on cleaning and normalizing the search volume values.
      - searchQuery: Saved as TEXT, no transformation required.
      - searchVolume: Google Trends represents search volume values with symbols such as 200K+ or 1000+.
        - 200K+ should be normalized to 200000.
        - 1000+ should be normalized to 1000.
    </br>
    We implemented the following transformation logic in Python:

    ```python
    if "K" in search_volume:
      search_volume = search_volume.replace("K+", "000")
    else:
      search_volume = search_volume.replace("+", "")
    ```
    After transformation, search_volume is stored as INT in the database.

  ***
      
</br>
</br>
  
  
  
- **Loading**
  ***
  To load the extracted and transformed data into our PostgreSQL database, we first define the schema using a models.sql file. This file creates (or verifies the existence of) the following tables:

    - videos
    - video_stats
    - trends_queries
    - etl_runs
  </br>
  Next, we use SQLAlchemy, a Python library that enables us to run SQL queries directly from our code.
  More details can be found in the Storage Layer section of this documentation
  [Storage Layer](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#storage-layer)
 
  </br>
  
  By leveraging SQLAlchemy, we can execute INSERT statements to load our processed data into the appropriate tables.

  **Insert Queries**

    - **YouTube Data**

      - Insert into the videos table:
        ```python
        conn.execute(text("""
                        INSERT INTO videos(video_id, title, description, channel_id, recorded_at, published_at)
                        VALUES (:video_id, :title, :description, :channel_id, :recorded_at, :published_at)   
                    """), {
                        "video_id": vid,
                        "title": snippet.get("title"),
                        "description": snippet.get("description"),
                        "channel_id": snippet.get("channelId"),
                        "published_at": snippet.get("publishedAt"),
                        "recorded_at": recorded_at    
                    })
        ```
      - Insert into the video_stats table:
        ```python
        conn.execute(text("""
                        INSERT INTO video_stats (video_id, recorded_at, view_count, like_count, comment_count)
                        VALUES (:video_id, :recorded_at, :view_count, :like_count, :comment_count)
                    """), {
                        "video_id": vid,
                        "recorded_at": recorded_at,
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)) if stats.get("likeCount") else None,
                        "comment_count": int(stats.get("commentCount", 0)) if stats.get("commentCount") else None,
                    })
        ```
        </br>
    - **Google Trends Data**
      
      - Insert into the trends_queries table:
        ```python
        conn.execute(text("""
                    INSERT INTO trends_queries(query, search_volume, region, category_id, retrieved_at)
                    VALUES (:query, :search_volume, :region, :category_id, :retrieved_at)    
                """), {
                    "query": query,
                    "search_volume": search_volume_int,
                    "region": REGION_CODE,
                    "category_id": 0,
                    "retrieved_at": recorded_at
                })
        ```
    </br>
    This structured loading process ensures that both YouTube and Google Trends data are consistently saved in PostgreSQL, making them available for downstream analysis and reporting.
    
  ***
  
</br>
</br>

### Storage layer



### Visualization

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
