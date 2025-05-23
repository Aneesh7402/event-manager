import datetime
from app.core.config import redis_client, REDIS_EVENTS_ZSET
from app.core.kafka_config import send_notification
from app.middleware.middleware import logger


async def poll_redis():
    """Poll Redis to check if the current timestamp >= event timestamps.
    If the condition is met, remove the event and trigger another function."""
    
    try:
        # Get the current UTC time
        current_timestamp = datetime.datetime.now(datetime.timezone.utc).timestamp()

        # Get the events from Redis sorted set where the score is less than or equal to the current timestamp
        events_to_process = redis_client.zrangebyscore(REDIS_EVENTS_ZSET, '-inf', current_timestamp)

        if not events_to_process:
            logger.info("No events to process. Nothing to remove.")
            return

        for event in events_to_process:
            event_id, event_type = event.decode().split(":")
            event_id = int(event_id)  # Get the event ID from the Redis key
            # Remove the event from Redis
            redis_client.zrem(REDIS_EVENTS_ZSET, event)

            # Log the event removal
            logger.info(f"Event {event_id} with type {event_type} removed from Redis.")

            # Call another function here
            await handle_event(event_id, event_type)

    except Exception as e:
        logger.error(f"Error occurred while polling Redis: {e}")


async def handle_event(event_id: int, event_type: str):
    """Handle the event by implementing your logic here."""

    logger.info(f"Handling event {event_id} of type {event_type}.")

    # Prepare the message payload, only containing the event_id
    message = {
        "event_id": event_id
    }

    # Based on the event type, choose the topic
    if event_type == "start":
        topic = "event_start"
    elif event_type == "end":
        topic = "event_end"
    else:
        topic = "send_notif"  # Default topic,

    # Publish the message to the respective Kafka topic
    send_notification(topic, message)

    logger.info(f"Message published to topic '{topic}' for event {event_id}.")
