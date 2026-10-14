from decouple import config

import redis.asyncio as redis

redis_client = redis.from_url(config("REDIS_URL"), decode_responses=True)
