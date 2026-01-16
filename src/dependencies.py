from fastapi import Depends
from redis.asyncio import Redis
from src import config
from src.services.github_client import GitHubClient
from src.services.openai_client import OpenAIClient
from src.services.code_review import CodeReview


async def get_redis_client():
    redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                         encoding="utf-8", decode_responses=True)
    return redis_client


async def get_review_service(redis_client: Redis = Depends(get_redis_client)):
    github_client = GitHubClient(config.GITHUB_TOKEN, redis_client)
    openai_client = OpenAIClient(config.OPENAI_API_TOKEN)
    return CodeReview(github_client, openai_client, redis_client)
    

