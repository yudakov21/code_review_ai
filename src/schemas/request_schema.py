from pydantic import BaseModel
from typing import Literal

class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: str
    candidate_level: Literal["Junior", "Middle", "Senior"]

    