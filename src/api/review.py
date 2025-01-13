import json

from src import config
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from src.schemas.request_schema import ReviewRequest
from src.services.github_client import GitHubClient
from src.services.openai_client import OpenAIClient
from src.services.code_review import CodeReview


router = APIRouter(
    prefix="/review",
    tags=["Review"]
    )

# Dependency function to get Redis
async def get_redis_client() -> Redis:
    redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, encoding="utf-8", decode_responses=True)
    return redis_client

async def get_review_service(redis_client: Redis = Depends(get_redis_client)):
    github_client = GitHubClient(config.GITHUB_TOKEN, redis_client)
    openai_client = OpenAIClient(config.OPENAI_API_TOKEN)
    return CodeReview(github_client, openai_client, redis_client)

@router.post("/")
async def review_data(
    data: ReviewRequest,
    review_service: CodeReview = Depends(get_review_service)):

    return await review_service.review_code(
        repo_url=data.github_repo_url,
        assignment=data.assignment_description,
        candidate_level=data.candidate_level,
    )


    

