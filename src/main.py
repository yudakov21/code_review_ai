from fastapi import FastAPI
from src.api.review import router as review_router


app = FastAPI(
    title="CodeReviewAI"
)

app.include_router(review_router)

