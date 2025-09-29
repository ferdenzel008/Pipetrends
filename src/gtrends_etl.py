from datetime import datetime, timezone
from db import get_engine
from config import REGION_CODE
from sqlalchemy import text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
from log_etl import log_etl_run   

logger = logging.getLogger("gtrends_etl")
logging.basicConfig(level=logging.INFO)


def get_trending_searches_ph():
    started_at = datetime.now(tz=timezone.utc)
    run_id = log_etl_run("get_trending_searches_ph", "running", started_at)

    try:
        # Set up Selenium Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # run without opening browser
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Go to Google Trends Philippines Trending Searches
        url = "https://trends.google.com/trending?geo=PH&hl=en-US&tz=360&sort=search-volume&hours=24"
        driver.get(url)
        time.sleep(10)  # wait for page to load (adjust if internet is slow)

        # Extract trending search titles
        trending_elements = driver.find_elements(By.CSS_SELECTOR, "div.mZ3RIc")
        search_volume_elem = driver.find_elements(By.CSS_SELECTOR, "div.lqv0Cb")

        trending = {
            i + 1: {
                "query": trendelem.text.strip(),
                "search_vol": volelem.text.strip()
            }
            for i, trendelem in enumerate(trending_elements) if trendelem.text.strip()
            for volelem in [search_volume_elem[i]] if i < len(search_volume_elem)
        }

        driver.quit()

        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("get_trending_searches_ph", "success", started_at, finished_at,
                    f"Fetched {len(trending)} trends", run_id)
        return trending

    except Exception as e:
        logger.error("Failed to fetch Google Trends", exc_info=True)
        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("get_trending_searches_ph", "failed", started_at, finished_at, str(e), run_id)
        return {}


def parse_and_upsert_trends(trending):
    started_at = datetime.now(tz=timezone.utc)
    run_id = log_etl_run("parse_and_upsert_trends", "running", started_at)

    try:
        engine = get_engine()
        recorded_at = datetime.now(tz=timezone.utc)

        with engine.begin() as conn:
            for rank, t in trending.items():
                query = t["query"]
                search_volume = t["search_vol"]

                # Normalize search volume
                if "K" in search_volume:
                    search_volume = search_volume.replace("K+", "000")
                else:
                    search_volume = search_volume.replace("+", "")

                try:
                    search_volume_int = int(search_volume)
                except ValueError:
                    logger.warning(f"Skipping invalid search_volume: {search_volume}")
                    continue

                # Insert query record
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

        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("parse_and_upsert_trends", "success", started_at, finished_at,
                    f"Upserted {len(trending)} queries", run_id)
        logger.info(f"Upserted {len(trending)} trending queries at {recorded_at.isoformat()}")

    except Exception as e:
        logger.error("Failed to upsert Google Trends data", exc_info=True)
        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("parse_and_upsert_trends", "failed", started_at, finished_at, str(e), run_id)


#if __name__ == "__main__":
#    searches = get_trending_searches_ph()
#    print("Trending Searches in PH:")
#    for rank, data in searches.items():
#        search_volume=data['search_vol']
#        if 'K' in search_volume:
#            search_volume=search_volume.replace("K+","000")
#        else:
#            search_volume=search_volume.replace("+","")
#        search_volume_int=int(search_volume)
#        print(f"{rank}. {data['query']} ({search_volume_int})")


