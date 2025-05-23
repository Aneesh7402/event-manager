from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

from starlette.middleware import Middleware

from app.services.kafka import create_kafka_topics
from app.services.kafka.start_consumers import start_all_consumers
from app.db import init_db
from app.services.cron import scrape_events, poll_redis
from app.middleware.middleware import JWTAuthMiddleware, logger
from app.api import auth,events
# Ensure the scheduler runs in the correct event loop
scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()  # Initialize your database here
    logger.info("Database initialized.")
    
    # Create kafka topics
    create_kafka_topics()
    
    # Define cron jobs to run during startup
    logger.info("Starting scheduler...")
    start_all_consumers()

    # First cron job (scrape events and populate Redis every 10 minutes)
    logger.info("Adding scrape_and_populate_redis job to scheduler...")
    scheduler.add_job(
        scrape_events,
        CronTrigger(minute="*"),  # Run every 10 minutes
        id="scrape_and_populate_redis",
        replace_existing=True
    )
    # Second cron job (poll Redis every minute)
    logger.info("Adding poll_redis_for_events job to scheduler...")
    scheduler.add_job(
        poll_redis,
        CronTrigger(minute="*"),  # Run every minute
        id="poll_redis_for_events",
        replace_existing=True
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")

    yield  # Application runs while inside this context

    # Shutdown logic (when the app shuts down)
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()
    logger.info("Scheduler shut down.")


app = FastAPI(
    lifespan=lifespan,
    middleware=[Middleware(JWTAuthMiddleware)]
)

app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
