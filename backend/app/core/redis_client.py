import logging
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

redis_manager = RedisManager()
