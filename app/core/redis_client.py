import redis.asyncio as redis
from app.core.config import settings
from typing import Optional
import json


class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        
    async def initialize(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
    async def close(self):
        if self.redis:
            await self.redis.close()
            
    async def get(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        return await self.redis.get(key)
        
    async def set(self, key: str, value: str, expire: int = 3600):
        if not self.redis:
            return False
        return await self.redis.set(key, value, ex=expire)
        
    async def delete(self, key: str):
        if not self.redis:
            return False
        return await self.redis.delete(key)
        
    async def get_json(self, key: str) -> Optional[dict]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
        
    async def set_json(self, key: str, value: dict, expire: int = 3600):
        return await self.set(key, json.dumps(value), expire)


redis_client = RedisClient()