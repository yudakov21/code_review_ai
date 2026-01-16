from dotenv import load_dotenv
import os


load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OPENAI_API_TOKEN = os.environ.get("OPENAI_API_TOKEN")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
