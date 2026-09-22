import redis.asyncio as redis

from decouple import config


redis_client = redis.from_url(config("REDIS_URL"))
