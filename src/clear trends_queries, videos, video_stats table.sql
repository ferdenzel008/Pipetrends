-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Data check SELECT queries~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SELECT * FROM video_stats ORDER BY recorded_at DESC, view_count DESC;
SELECT video_id, title, description, recorded_at, published_at FROM videos ORDER BY recorded_at DESC, title DESC;
SELECT * FROM trends_queries ORDER BY retrieved_at DESC;
SELECT * FROM etl_runs ORDER BY started_at;
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-- ~~~~~~~~~~~~~~~~~~~~~~Latest logs of etl run~~~~~~~~~~~~~~~~~~~~~~~ 
with cte as (SELECT * FROM etl_runs ORDER BY id DESC LIMIT 7)
SELECT * from cte ORDER BY started_at;
-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UPDATE video_stats SET recorded_at = '2025-09-19 22:01:00.657287+08' WHERE CAST(TO_CHAR(recorded_at, 'YYYY-MM-DD') AS DATE) = '2025-09-20';

SELECT query,TO_CHAR(trends_queries.retrieved_at, 'YYYY-MM-DD HH12:MI:SS AM') AS formatted_retrieved_at, search_volume FROM trends_queries 
WHERE CAST(TO_CHAR(retrieved_at, 'YYYY-MM-DD') AS DATE) = '2025-09-29';


















Delete FROM video_stats WHERE 1=1;
Delete FROM videos WHERE 1=1;
Delete FROM trends_queries WHERE 1=1;
DELETE FROM etl_runs WHERE 1=1;

DELETE FROM trends_queries WHERE CAST(TO_CHAR(retrieved_at, 'YYYY-MM-DD') AS DATE) = '2025-09-22';
DELETE FROM videos WHERE CAST(TO_CHAR(recorded_at, 'YYYY-MM-DD') AS DATE) = '2025-09-22';
DELETE FROM video_stats WHERE CAST(TO_CHAR(recorded_at, 'YYYY-MM-DD') AS DATE) = '2025-09-22';