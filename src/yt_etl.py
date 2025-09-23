import os
import logging
from googleapiclient.discovery import build
from sqlalchemy import text
from datetime import datetime, timezone
from db import get_engine
from config import YOUTUBE_API_KEY, REGION_CODE
from log_etl import log_etl_run

logger = logging.getLogger("youtube_etl")
logging.basicConfig(level=logging.INFO)


def fetch_most_popular_videos(region=REGION_CODE, max_results=50):
    """Fetch trending YouTube videos via API"""
    started_at = datetime.now(tz=timezone.utc)
    run_id = log_etl_run("fetch_most_popular_videos", "running", started_at)

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        results = []
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region,
            maxResults=min(max_results, 25)
        )
        response = request.execute()
        results.extend(response.get("items", []))

        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("fetch_most_popular_videos", "success", started_at, finished_at,
                    f"Fetched {len(results)} videos", run_id)
        return results

    except Exception as e:
        logger.error("YouTube API request failed", exc_info=True)
        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("fetch_most_popular_videos", "failed", started_at, finished_at, str(e), run_id)
        return []


def parse_and_upsert(videos):
    """Insert YouTube video metadata & stats into database"""
    started_at = datetime.now(tz=timezone.utc)
    run_id = log_etl_run("parse_and_upsert", "running", started_at)

    try:
        engine = get_engine()
        recorded_at = datetime.now(tz=timezone.utc)

        with engine.begin() as conn:
            for v in videos:
                vid = v.get("id")
                if not vid:
                    logger.warning("Skipping video with missing ID")
                    continue

                snippet = v.get("snippet", {})
                stats = v.get("statistics", {})

                try:
                    # Upsert video
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

                    # Insert stats snapshot
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

                except Exception:
                    logger.error(f"Failed to upsert video {vid}", exc_info=True)

        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("parse_and_upsert", "success", started_at, finished_at,
                    f"Upserted {len(videos)} videos", run_id)
        logger.info(f"Upserted {len(videos)} videos at {recorded_at.isoformat()}")

    except Exception as e:
        logger.error("Database transaction failed", exc_info=True)
        finished_at = datetime.now(tz=timezone.utc)
        log_etl_run("parse_and_upsert", "failed", started_at, finished_at, str(e), run_id)
