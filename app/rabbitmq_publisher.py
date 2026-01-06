import json
import pika
import os
from typing import Optional

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

# 1. Setup global connection/channel (or use a singleton pattern)
def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="payment_confirmed", durable=True)
    return connection, channel

def publish_payment_confirmed(payment_id: int, order_id: int, status: str, user_id: str, amount: float, tenant_id: Optional[str] = None) -> None:
    connection = None
    try:
        # Set a 5-second timeout so your web app doesn't hang
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            heartbeat=600, 
            blocked_connection_timeout=300,
            connection_attempts=3,
            retry_delay=1
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.queue_declare(queue="payment_confirmed", durable=True)
        
        event = {
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_status": status,
            "user_id": user_id,
            "amount": amount
        }
        if tenant_id is not None:
            event["tenant_id"] = tenant_id

        channel.basic_publish(
            exchange="",
            routing_key="payment_confirmed",
            body=json.dumps(event).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        print(f"Successfully published order {order_id}")

    except pika.exceptions.AMQPConnectionError:
        print("ERROR: Could not connect to RabbitMQ. Check if the service is running.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
