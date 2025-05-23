from datetime import datetime

from kafka.admin import NewTopic
from sqlalchemy.orm import Session

from app.core.kafka_config import kafka_admin_client
from app.db.session import get_db
from app.repositories.auth import get_users_by_ids
from app.repositories.event import get_first_scheduled_event, get_accesses_by_event
from app.services.events import add_next_event
from app.services.mail_service import send_bulk_email
from app.utils import EventStatus, get_message, TOPICS_TO_CREATE


def create_kafka_topics():
    """Create Kafka topics if they do not exist."""
    existing_topics = set(kafka_admin_client.list_topics())  # Get the list of current topics
    topics_to_create_filtered = [
        NewTopic(name=topic, num_partitions=1, replication_factor=1)
        for topic in TOPICS_TO_CREATE if topic not in existing_topics
    ]

    if topics_to_create_filtered:
        kafka_admin_client.create_topics(new_topics=topics_to_create_filtered, validate_only=False)
        print(f"Created topics: {', '.join([topic.name for topic in topics_to_create_filtered])}")
    else:
        print("All topics already exist.")

def handle_db_update_start(msg: dict):
    event_id = msg.get("event_id")
    db: Session = next(get_db())
    event = get_first_scheduled_event(db, event_id)
    if event:
        event.status = EventStatus.ACTIVE.value
        db.commit()
    db.flush()
    add_next_event(db, event_id)

def handle_db_update_end(msg: dict):
    event_id = msg.get("event_id")
    db: Session = next(get_db())
    event = get_first_scheduled_event(db, event_id)
    if event:
        event.status = EventStatus.COMPLETED.value
        db.commit()
    db.flush()

def handle_notification_push(msg: dict):
    event_id = msg.get("event_id")
    topic = msg.get("topic")
    db: Session = next(get_db())
    # Get all accesses for the event
    accesses = get_accesses_by_event(db, event_id)

    # Extract user_ids from those access records
    user_ids = {access.user_id for access in accesses}  # no need for int() if already int
    # Fetch users with those IDs
    users = get_users_by_ids(db, user_ids)
    subject,message=get_message(topic, event_id, datetime.now())
    send_bulk_email([user.email for user in users],subject,message)







