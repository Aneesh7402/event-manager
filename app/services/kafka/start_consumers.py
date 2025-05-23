from app.core.kafka_config import start_kafka_consumer
from app.services.kafka import handle_db_update_start, handle_notification_push, handle_db_update_end


def start_all_consumers():
    # Consumers for event_start
    start_kafka_consumer("event_start", "start-updater", handle_db_update_start)
    start_kafka_consumer("event_start", "notif-pusher-start", handle_notification_push)

    # Consumers for event_end
    start_kafka_consumer("event_end", "end-updater", handle_db_update_end)
    start_kafka_consumer("event_end", "notif-pusher-end", handle_notification_push)

    # Consumer for send_notif
    start_kafka_consumer("send_notif", "notif-pusher-direct", handle_notification_push)