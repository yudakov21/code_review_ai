import json
import aiohttp

from redis.asyncio import Redis

class GitHubClient:
    def __init__(self, github_token: str, redis_client: Redis):
        self.github_token = github_token
        self.redis_client = redis_client
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def parse_parts_url(self, url: str):
        if not url.startswith("https://github.com/"):
            raise ValueError("URL is not a valid GitHub repository")
        
        parts = url.replace("https://github.com/", "").split("/")

        if len(parts) < 2:
            raise ValueError("Incorrect URL format")
        return parts[0], parts[1]
    
    async def fetch_file_content(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Error downloading a file")
                    text = await response.text()
                    return text
            except Exception as e:
                raise RuntimeError(f"Error downloading a file: {str(e)}") 

    async def fetch_repo_content(self, url: str):
        cache_key = f"repo_cache:{url}"
        cached_data = await self.redis_client.get(cache_key)

        if cached_data is not None:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                # Delete corrupted data from the cache
                await self.redis_client.delete(cache_key)
                print(f"Invalid cache data for key: {cache_key}")

        try:
            owner, repo = self.parse_parts_url(url)
        except ValueError as e:
            raise RuntimeError(f"Incorrect GitHub URL: {str(e)}")
        
        async with aiohttp.ClientSession() as session:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            try:    
                async with session.get(url=api_url, headers=self.headers) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise RuntimeError(f"Error GitHub API: {text}")
                    files = await response.json()
            except ValueError as e:
                raise RuntimeError(f"Incorrect GitHub URLL: {str(e)}")

        found_files = []
        files_content = []
        for info in files:
            if info["type"] == "file":
                filename = info["name"]
                found_files.append(filename) 
                
                content = await self.fetch_file_content(info["url"])
                files_content.append(f"File:{filename}\n{content}\n")
        
        repo_data = {
            "found_files": found_files,
            "files_content": files_content
        }  
    
        await self.redis_client.set(cache_key, json.dumps(repo_data), ex=3600)
        return repo_data