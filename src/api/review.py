from fastapi import APIRouter, Depends
from src.schemas.request_schema import ReviewRequest
from src.services.code_review import CodeReview
from src.dependencies import get_review_service


router = APIRouter(
    prefix="/review",
    tags=["Review"]
    )


@router.post("/")
async def review_data(
    data: ReviewRequest,
    review_service: CodeReview = Depends(get_review_service)):

    return await review_service.review_code(
        repo_url=data.github_repo_url,
        assignment=data.assignment_description,
        candidate_level=data.candidate_level,
    )


    

