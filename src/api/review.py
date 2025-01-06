import json

from src import config
from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from src.schemas.request_schema import ReviewRequest
from src.services.github_client import GitHubClient
from src.services.openai_client import OpenAIClient


router = APIRouter(
    prefix="/review",
    tags=["Review"]
    )

# Dependency function to get Redis
async def get_redis_client() -> Redis:
    redis_client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, encoding="utf-8", decode_responses=True)
    return redis_client

@router.post("/")
async def review_data(
    data: ReviewRequest,
    redis_client: Redis = Depends(get_redis_client)
):
    cache_key = f"review_result:{data.github_repo_url}:{data.assignment_description}:{data.candidate_level}"

    cached_result = await redis_client.get(cache_key)
    if cached_result is not None:
        try:
            return {"cached": True, **json.loads(cached_result)}
        except json.JSONDecodeError as e:
            print(f"Error decoding cached data: {e}")
            # Delete corrupted data from the cache
            await redis_client.delete(cache_key)

    github_client = GitHubClient(config.GITHUB_TOKEN, redis_client)
    openai_client = OpenAIClient(config.OPENAI_API_TOKEN)

    try:
        repo_result = await github_client.fetch_repo_content(data.github_repo_url)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    code_text = "\n".join(repo_result["files_content"])

    try:
        review_result = openai_client.analyze_code(
            code_text=code_text,
            assignment=data.assignment_description,
            candidate_level=data.candidate_level
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response_data = {
        "found_files": repo_result["found_files"],
        "review_result": review_result
    }

    await redis_client.set(cache_key, json.dumps(response_data), ex=3600)
    return {"cached": False, **response_data}
    

