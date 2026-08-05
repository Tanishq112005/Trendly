import logging
import json
import redis.asyncio as redis
from app.core.config import REDIS_URI


class RedisManager:
    client = None

    @classmethod
    async def connect(cls):
        if REDIS_URI:
            cls.client = redis.from_url(REDIS_URI)
            await cls.client.ping()
            logging.info("Connected to Redis.")
        else:
            logging.warning("REDIS_URI not set. Redis is not connected.")

    @classmethod
    async def disconnect(cls):
        if cls.client:
            await cls.client.close()
            logging.info("Disconnected from Redis.")

    @classmethod
    async def publish_ticket(cls, session_id: str, ticket_id: int):
        """Publish a ticket event to Redis Pub/Sub."""
        if not cls.client:
            logging.warning("Cannot publish ticket: Redis not connected.")
            return

        try:
            payload = json.dumps({"session_id": session_id, "ticket_id": ticket_id})
            await cls.client.publish("ticket_events", payload)
            logging.info(
                f"Published ticket event for session {session_id}, ticket {ticket_id}"
            )
        except Exception as e:
            logging.error(
                f"Failed to publish ticket event to Redis (network drop or timeout): {e}"
            )


redis_manager = RedisManager()
