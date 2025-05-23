import datetime
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.db.models import Event
from app.core.config import redis_client, REDIS_EVENTS_ZSET  # Redis client
from app.db.session import get_db
from app.middleware.middleware import logger

async def scrape_events():
    """Scrape events from the database that are within the current and next cron window,
    and add them to Redis sorted set."""
    db=next(get_db())
    try:
        # Define the current time (UTC) and the next cron window (10 minutes ahead)
        now = datetime.datetime.now(datetime.timezone.utc)
        next_cron_time = now + datetime.timedelta(minutes=10)  # Next 10 minutes

        # Query the database for events whose start_time is within the cron window
        events_in_window = db.query(Event).filter(
            Event.start_time >= now,
            Event.start_time <= next_cron_time
        ).all()

        # If there are no events, log and return
        if not events_in_window:
            logger.info("No events found for the current cron window.")
            return

        # Define a polling timestamp to track the next cron window
        polling_timestamp = next_cron_time.timestamp()

        # Add events to Redis sorted set
        for event in events_in_window:
            start_timestamp = event.start_time.timestamp()
            end_timestamp = event.end_time.timestamp()

            # Add event start and end times to the Redis sorted set
            redis_client.zadd(
                REDIS_EVENTS_ZSET,
                {f"{event.id}:start": start_timestamp}
            )
            redis_client.zadd(
                REDIS_EVENTS_ZSET,
                {f"{event.id}:end": end_timestamp}
            )

        # Log that the scraping has completed
        logger.info(f"Scraped and added {len(events_in_window)} events to Redis.")

        # Return the polling timestamp for future checks
        return polling_timestamp

    except Exception as e:
        logger.error(f"An error occurred while scraping events: {e}")
        return None
