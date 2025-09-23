import logging
from datetime import datetime, timezone
from db import create_tables
from yt_etl import fetch_most_popular_videos, parse_and_upsert
from gtrends_etl import get_trending_searches_ph, parse_and_upsert_trends
from config import REGION_CODE
from log_etl import log_etl_run  

logger = logging.getLogger("etl_runner")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def run_all():
    create_tables()

    # Track overall ETL job
    estarted_at = datetime.now(tz=timezone.utc)
    etl_run_id = log_etl_run("full_etl_run", "running", estarted_at)

    try:
        # YouTube ETL
        ystarted_at = datetime.now(tz=timezone.utc)
        yt_run_id = log_etl_run("youtube_etl", "running", ystarted_at)

        try:
            videos = fetch_most_popular_videos(region=REGION_CODE)
            parse_and_upsert(videos)
            log_etl_run("youtube_etl", "success", ystarted_at, datetime.now(tz=timezone.utc), details=f"Fetched {len(videos)} videos",run_id=yt_run_id)
        except Exception as e:
            logger.error("YouTube ETL failed", exc_info=True)
            log_etl_run("youtube_etl", "failed", ystarted_at, datetime.now(tz=timezone.utc), details=str(e),run_id=yt_run_id)

        # Google Trends ETL
        tstarted_at = datetime.now(tz=timezone.utc)
        gt_run_id = log_etl_run("gtrends_etl", "running", tstarted_at)
        try:
            trending = get_trending_searches_ph()
            parse_and_upsert_trends(trending)
            log_etl_run("gtrends_etl", "success", tstarted_at, datetime.now(tz=timezone.utc), details=f"Fetched {len(trending)} queries",run_id=gt_run_id)
        except Exception as e:
            logger.error("Google Trends ETL failed", exc_info=True)
            log_etl_run("gtrends_etl", "failed", tstarted_at, datetime.now(tz=timezone.utc), details=str(e),run_id=gt_run_id)

        # Overall success
        log_etl_run("full_etl_run", "success", estarted_at, datetime.now(tz=timezone.utc), details="ETL run completed",run_id=etl_run_id)

    except Exception as e:
        logger.error("ETL runner crashed", exc_info=True)
        log_etl_run("full_etl_run", "failed", estarted_at, datetime.now(tz=timezone.utc), details=str(e),run_id=etl_run_id)


if __name__ == "__main__":
    with open("D:/yt_beauty_trends/logs/etl.log", "a") as f:
        f.write("-" * 80 + "\n")

    run_all()
    logger.info("ETL run complete")

    with open("D:/yt_beauty_trends/logs/etl.log", "a") as f:
        f.write("-" * 80 + "\n\n")