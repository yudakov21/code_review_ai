import json
from fastapi import HTTPException
from redis.asyncio import Redis
from src.services.github_client import GitHubClient
from src.services.openai_client import OpenAIClient

class CodeReview:
    def __init__(self, github_client: GitHubClient , openai_client: OpenAIClient, redis_client: Redis):
        self.github_client = github_client
        self.openai_client = openai_client
        self.redis_client = redis_client

    async def review_code(self, repo_url: str, assignment: str, candidate_level: str ):
        cache_key = f"review_result:{repo_url}:{assignment}:{candidate_level}"

        cache_data = await self.redis_client.get(cache_key)
        if cache_data is not None:
            try:
                return {"cached_data": True, **json.loads(cache_data)}
            except json.JSONDecodeError as e:
                print(f"Error decoding cached data: {e}")
                # Delete corrupted data from the cache
                await self.redis_client.delete(cache_key)

        try:
            repo_data = await self.github_client.fetch_repo_content(repo_url)
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        code_text = "\n".join(repo_data["files_content"])

        try:
            review_result = self.openai_client.analyze_code(
                code_text=code_text,
                assignment=assignment,
                candidate_level=candidate_level
            )
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        response_data = {
            "found_files": repo_data["found_files"],
            "review_result": review_result
        }    

        await self.redis_client.set(cache_key, json.dumps(response_data), ex=3600)
        return {"cached_data": False, **response_data}

