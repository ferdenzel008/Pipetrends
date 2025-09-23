import logging
from sqlalchemy import text
from db import get_engine

logger = logging.getLogger("etl_logger")

def log_etl_run(job_name, status, started_at, finished_at=None, details=None, run_id=None):
    #Insert or update ETL run record in etl_runs table
    try:
        engine = get_engine()
        with engine.begin() as conn:
            if status == "running" and run_id is None:
                # Insert new ETL run record
                result = conn.execute(text("""
                    INSERT INTO etl_runs (job_name, status, started_at, details)
                    VALUES (:job_name, :status, :started_at, :details)
                    RETURNING id
                """), {
                    "job_name": job_name,
                    "status": status,
                    "started_at": started_at,
                    "details": details
                })
                run_id = result.scalar()
                logger.info(f"Started ETL job '{job_name}' with run_id={run_id}")
                return run_id
            else:
                # Update ETL run record
                conn.execute(text("""
                    UPDATE etl_runs
                    SET status = :status,
                        finished_at = :finished_at,
                        details = :details
                    WHERE id = :id
                """), {
                    "id": run_id,
                    "status": status,
                    "finished_at": finished_at,
                    "details": details
                })
                logger.info(f"Updated ETL job '{job_name}' run_id={run_id} to status={status}")
                return run_id
    except Exception as e:
        logger.error(f"Failed to log ETL run for job '{job_name}'", exc_info=True)
        return run_id