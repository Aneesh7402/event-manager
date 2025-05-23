import threading

from kafka import KafkaProducer, KafkaAdminClient, KafkaConsumer
import json
import os
from dotenv import load_dotenv

from app.middleware.middleware import logger

# Load environment variables from .env file (if present)
load_dotenv()

# Get Kafka configuration from environment variables
bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")  # Default to localhost:9092
client_id = os.getenv("KAFKA_CLIENT_ID", "fastapi-client")  # Default to 'fastapi-client'

# Create Kafka producer using environment variables
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Create Kafka AdminClient using environment variables
kafka_admin_client = KafkaAdminClient(
    bootstrap_servers=bootstrap_servers,
    client_id=client_id
)

def send_notification(topic: str, data: dict):
    """Send a message to a specific Kafka topic."""
    data.update({"topic": topic})
    try:
        future = producer.send(topic, value=data)
        result = future.get(timeout=10)  # Block until the message is sent or timeout
        return result
    except Exception as e:
        # You can optionally use your logger here
        logger.error(f"Failed to send message to Kafka topic '{topic}': {e}")
        return None
    



def start_kafka_consumer(topic: str, group_id: str, handler_fn):
    """
    Factory to start a Kafka consumer thread.

    Args:
        topic (str): Kafka topic to subscribe to.
        group_id (str): Consumer group ID (must be unique per logical consumer).
        handler_fn (function): Function that handles the consumed message. Signature: handler_fn(message_value: dict)
    """
    def consumer_thread():
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id=group_id,
            auto_offset_reset='earliest',  # Optional: use 'latest' in production if needed
            enable_auto_commit=True
        )

        logger.info(f"Started Kafka consumer on topic '{topic}' with group '{group_id}'")
        for message in consumer:
            try:
                handler_fn(message.value)
            except Exception as e:
                logger.error(f"Error handling Kafka message: {e}")

    # Start the consumer in a daemon thread
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
