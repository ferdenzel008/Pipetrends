# Pipetrends

An automated tool for daily extraction of most popular Youtube video and Google trends using Python. 

## Table of Contents
- [Introduction](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#introduction)
- [System Architecture](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#system-architecture)
- [Data Sources](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#data-sources)
- [ETL Logic](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#etl-logic-extract-transform-load)
- [Storage Layer](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#storage-layer)
- [Visualization](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#visualization)
- [Configuration](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#configuration)
- [How to Run](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#how-to-run)
- [Limitations & Future Improvements](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#limitations--future-improvements)
- [Contributing](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#contributing)
- [References](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#references)


## Introduction

Pipetrends is a data pipeline project that collects and processes trending information from two major sources:
- YouTube Data API: to retrieve trending videos and related analytical data.
- Google Trends (via Selenium web scraping): to capture real-time search trends along with the search volume for each search trends.

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

![Project Architecture Diagram](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/images/Project%20Architecture.jpg)

</br>

### Data Sources

- **Youtube**
  ***
  For this project, YouTube serves as a primary source of trending video content. Since the pipeline is designed to highlight what’s relevant to a local audience, we focus specifically on the Philippines (PH) region. By doing this, we capture the most popular and relevant videos trending within that geographic area.

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
  
  Next, we use SQLAlchemy, a Python library that enables us to run SQL queries directly from our code. More details can be found in the [Storage Layer](https://github.com/ferdenzel008/Pipetrends/blob/main/docs/readme.md#storage-layer) section of this documentation. 
 
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
 In this section, we describe the database setup and schema definitions used to persist the extracted and transformed data. We are using PostgreSQL as our database.

 - **Database Setup**

   ***

   PostgreSQL needs to be installed and run locally. To create a database for this project:

   1. Install PostgreSQL (via package manager, installer, or Docker).
   2. Start the PostgreSQL service.
   3. Create a new database (Take note of the DB name for the DATABASE_URL in the .env file)
   4. (Optional) Create a dedicated user with permissions (Take note of the DB name for the DATABASE_URL in the .env file)

   This sets up a local PostgreSQL environment to host our ETL pipeline data.

   ***

</br>

 - **Schema Definition**
   
   ***
   
   We define our database schema in the src/models.sql file. This file creates (or verifies) the required tables and extensions:
   ```python
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

   CREATE TABLE IF NOT EXISTS videos (
       id BIGSERIAL PRIMARY KEY,
       video_id TEXT,
       title TEXT,
       description TEXT,
       channel_id TEXT,
       recorded_at TIMESTAMPTZ NOT NULL,
       published_at TIMESTAMPTZ,
       category_id TEXT
   );
   
   CREATE TABLE IF NOT EXISTS video_stats (
       id BIGSERIAL PRIMARY KEY,
       video_id TEXT REFERENCES videos(video_id),
       recorded_at TIMESTAMPTZ NOT NULL,
       view_count BIGINT,
       like_count BIGINT,
       comment_count BIGINT,
       UNIQUE (video_id, recorded_at)
   );
   
   CREATE TABLE IF NOT EXISTS trends_queries (
       id BIGSERIAL PRIMARY KEY,
       query TEXT NOT NULL,
       search_volume BIGINT,
       region TEXT,
       category_id TEXT,
       retrieved_at TIMESTAMPTZ NOT NULL DEFAULT now()
   );
   
   CREATE TABLE IF NOT EXISTS etl_runs (
       id BIGSERIAL PRIMARY KEY,
       job_name TEXT,
       status TEXT,
       started_at TIMESTAMPTZ,
       finished_at TIMESTAMPTZ,
       details TEXT
   );
   ```
   - videos: Stores basic metadata about each YouTube video.
   - video_stats: Stores daily/hourly snapshots of video engagement metrics.
   - trends_queries: Stores trending Google search queries and their volumes.
   - etl_runs: Logs metadata about ETL job executions (useful for monitoring).
     
   ***

</br>

 - **Database Connection**

   ***

   We use SQLAlchemy to interact with PostgreSQL. SQLAlchemy allows us to:

    - Create an engine (connection to the database).
    - Run raw SQL queries.
    - Initialize or verify tables.

   We defined the necessary functions for the database connection on the src/db.py
   ```python
   def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, echo=False, future=True)
    return _engine

   def create_tables():
    engine = get_engine()
    with engine.begin() as conn, open("src/models.sql") as f:
        sql = f.read()
        conn.execute(text(sql))
    logging.info("Tables created/verified.")
    ```
     - get_engine(): Creates a SQLAlchemy engine that can be reused throughout the project.
     - create_tables(): Reads models.sql and executes it, ensuring all required tables exist before loading data.

    ***
   
 - **Database Design**

   ***

   ![Database Schema Diagram](https://github.com/ferdenzel008/Pipetrends/blob/2e731fa8a12972d11006b39e38f1cb8567168742/images/Database%20Schema%20Diagram.png)

   This database is structured to support tracking YouTube video data , Google Trends data, and ETL processes.

    - videos
       
      - Stores metadata about each YouTube video such as video_id, title, description, channel_id, and timestamps (recorded_at, published_at).
      - Acts as the central table, with other tables referencing it through video_id.

    - video_stats
       
      - Contains time-series data of a video’s performance: view_count, like_count, and comment_count.
      - Each record is tied to a video_id and a recorded_at timestamp, allowing historical trend tracking.
      - The (video_id, recorded_at) pair is unique, ensuring no duplicate statistics for the same video snapshot.

    - trends_queries
       
      - Stores trending search queries from Google Trends (or similar sources).   
      - Fields like query, search_volume, region, and category_id help capture contextual data.     
      - retrieved_at shows when the data was collected, supporting time-based trend analysis.
    
    - etl_runs
       
      - Logs ETL pipeline executions.   
      - Tracks job name, status, start and finish times, and optional details for monitoring and debugging.

    ***
      
</br>
</br>

### Visualization

Word Cloud                 |  Content Gaps             | Trend Alignment
:-------------------------:|:-------------------------:|:-------------------------:
![](https://github.com/ferdenzel008/Pipetrends/blob/main/sampleoutputs/wordcloud.png)  |  ![](https://github.com/ferdenzel008/Pipetrends/blob/main/sampleoutputs/contentgaps.png) | ![](https://github.com/ferdenzel008/Pipetrends/blob/main/sampleoutputs/trend_alignment.png)

 The visualizations highlight insights from YouTube and Google Trends data.
 
 - **Word Cloud (YouTube Trending Keywords)**
 This chart shows the most frequent keywords from today’s trending YouTube content. Larger words indicates higher frequency and stronger influence in current trends.
 
 - **Content Gaps (Google Trends vs. YouTube Trending)**
 The horizontal bar chart identifies the top 10 trending search queries from Google Trends that are not reflected in YouTube trending content. This reveals opportunities for content creators to address gaps.”
 
 - **Trend Alignment (YouTube vs. Google Trends)**
 The bubble chart compares the volume of keywords between YouTube Trending and Google Trends. The large bubble for YouTube Trending illustrates its higher keyword count, while the smaller Google Trends bubble shows fewer overlapping topics, emphasizing misalignment between the two platforms.
 
 These outputs are automatically saved in the notebooks/outputs/ folder. They will only appear after running all the cells in the dashboard.ipynb file.

 - **About dashboard.ipynb**
 
   The dashboard.ipynb notebook acts as the central workflow for this project. It:
   
   - Connects to the local PostgreSQL database using SQLAlchemy to retrieve trend data,
   - Processes and cleans the data with pandas,
   - Generates visualizations with matplotlib (and supporting libraries),
   - Exports the resulting charts and word clouds into the notebooks/outputs/ folder for reporting and presentation.
   
   This notebook serves as both the analysis pipeline and the dashboard generator for the project.

</br>
</br>

## Configuration

 Here are the variables defined in the .env file:
 
  - **YOUTUBE_API_KEY**
  
    - Stores the API key used to authenticate requests to the YouTube Data API v3.
    - Required for retrieving trending video data and related metadata.
  
  - **DATABASE_URL**
  
    - Defines the connection string for the local PostgreSQL database.
    - The format is:
      ```python
      postgresql://<username>:<password>@localhost:<port>/<dbname>
      ```
    - This allows SQLAlchemy to connect to the database and retrieve/store data.
  
  - **REGION_CODE**
  
    - Specifies the target region for data collection (in this case, PH for the Philippines).
    - Ensures that API queries are region-specific, returning localized trends.
    - This makes changing the region much easier — users only need to update the REGION_CODE value in the .env file (e.g., US, JP, IN), instead of modifying the source code.

</br>
</br>

## How to Run
 
 1. Clone the repository
    ```python
    git clone https://github.com/ferdenzel008/Pipetrends.git
    cd Pipetrends
    ```
 2. Create a virtual environment
    ```python
    python3 -m venv venv 
    source venv/bin/activate   # Use for Linux/macOS
    venv\Scripts\activate      # Use for Windows
    ```
 3. Create .env file (use [sample.env.txt file](https://github.com/ferdenzel008/Pipetrends/blob/main/sample.env.txt) as guide)
 4. Download and install PostgreSQL from the official website:
    https://www.postgresql.org/download/

 5. Use the Default Superuser
   PostgreSQL comes with a default superuser account called postgres. You can use this account directly instead of creating a new user. During installation, you are asked to set a password for this account.

 6. Create a Database in pgAdmin

    1. Open pgAdmin and connect to your local PostgreSQL server using the postgres superuser account.
    2. In the left-hand tree, expand Databases, right-click, and select Create > Database.
    3. Enter a name for your new database (for example, pipetrendsdb).
    4. In the Owner dropdown, leave it as postgres since you are using the superuser account.
    5. Save to create the database.

 7. Update the .env file

    Use the postgres superuser credentials in your .env file under DATABASE_URL. The format is:
   
    postgresql://postgres:<your_password>@localhost:<port>/pipetrendsdb
     - port is usually set to 5432

 9. Execute the [run_etl.sh script](https://github.com/ferdenzel008/Pipetrends/blob/main/scripts/run_etl.sh) 
    ```bash
    bash run_etl.sh
    ```
 
    This script will automatically run the entire project pipeline from data extraction to loading into the database, except for the visualization part which must be generated separately through the dashboard.ipynb notebook.
 
 - **Optional Scheduling the Script**
 
   To automate daily runs, you can set up a scheduling tool of your choice. For example:
   
   - On Linux or macOS you can use cron jobs
   - On Windows you can use Task Scheduler (this project uses Task Scheduler to run run_etl.sh once per day)
   
   This ensures that data is refreshed regularly without requiring manual execution.

</br>
</br>

## Limitations and Future Improvements

**Limitations**

* **YouTube Data API Quotas**
  The project depends on the YouTube Data API v3, which enforces daily quota limits. These quotas may restrict the number of requests that can be made in a single day. Users should be aware of this limitation when running the ETL pipeline. Although videos.list method cost 1 unit per call, it is still advisable to watchout specially in development phase. For more details, see [YouTube Data API Quotas](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits).

**Future Improvements**

1. **Dashboard Enhancements**
   The current visualization is implemented in Jupyter Notebook. A more interactive and user-friendly dashboard could be developed using tools such as **Streamlit**, **Dash**, or **Power BI** to provide better accessibility and presentation.

2. **Cloud Deployment**
   Running the project locally limits scalability. Migrating to a cloud environment (e.g., AWS, GCP, or Azure) would allow automated scheduling, better resource management, and easier collaboration.

3. **Database Backup**
   At present, database backup may need to be done manually. Future improvements could include automated database backup strategies (e.g., scheduled dumps, cloud-based replication, or containerized backup solutions).

4. **Email Notifications for Log Failures**
   Currently, failures or errors must be manually checked through logs. A future enhancement would be to implement an email notification system that alerts the user when the ETL pipeline encounters issues.

These improvements would make the project more robust, scalable, and user-friendly for long-term use.



## Contributing

   This project was created as part of my personal portfolio to showcase my skills and workflow. For that reason, I am not accepting external contributions at this time.
   
   I truly appreciate your interest, and if you find this project helpful or inspiring, feel free to use it as a reference for your own work.

## References

   Google. (n.d.). *YouTube Data API overview*. Google for Developers. Retrieved September 29, 2025, from [https://developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)
   
   Bovan, A. (n.d.). *Parts of speech word lists*. Ashley Bovan. Retrieved September 29, 2025, from [http://www.ashley-bovan.co.uk/words/partsofspeech.html](http://www.ashley-bovan.co.uk/words/partsofspeech.html)
   
   Google. (n.d.). *Google Trends – Philippines*. Google Trends. Retrieved September 29, 2025, from [https://trends.google.com/trending?geo=PH&hl=en-US](https://trends.google.com/trending?geo=PH&hl=en-US)
