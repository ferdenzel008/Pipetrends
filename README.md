<p align="center">
 
  <a source="https://github.com/ferdenzel008/Pipetrends/tree/main/docs"><img src="https://github.com/ferdenzel008/Pipetrends/blob/main/images/Pipetrends.png" height="400"></a>
 
</p>

***

Pipetrends provides you with a tool that can extract most popular youtube videos using the Youtube Data API and extract google trends using the Selenium library. 

## Features
- Collects trending Youtube videos via Youtube Data API v3 (daily)
- Collects trending searches on Google daily via Selenium (daily)
- Stores data in a database
- Alert and monitoring of data pipeline (**<ins>In development</ins>**)
- Provides data transformation for analytics
- Enables visualization with Jupyter notebook

## Project Architecture
![Project Architecture Diagram](https://github.com/ferdenzel008/Pipetrends/blob/main/images/Project%20Architecture.jpg)

## Tech Stack
- Youtube Data API v3
- Python
- Selenium
- SQLAlchemy
- PostgreSQL
- Jupyter Notebook

## Quick Start

### Installation

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

 8. Execute the [run_etl.sh script](https://github.com/ferdenzel008/Pipetrends/blob/main/scripts/run_etl.sh) 
    ```bash
    bash run_etl.sh
    ```
 
    This script will automatically run the entire project pipeline from data extraction to loading into the database, except for the visualization part which must be generated separately through the dashboard.ipynb notebook.
 
 - Optional Scheduling the Script
 
   To automate daily runs, you can set up a scheduling tool of your choice. For example:
   
   - On Linux or macOS you can use cron jobs
   - On Windows you can use Task Scheduler (this project uses Task Scheduler to run run_etl.sh once per day)
   
   This ensures that data is refreshed regularly without requiring manual execution.

