import json

from unittest.mock import patch


def test_review_endpoint_cached(test_client, mock_redis):
    cached_data = {
        "found_files": ["file1.py"],
        "review_result": {"review": "Good code"}
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    with patch("src.api.review.get_redis_client", return_value=mock_redis):
        payload = {
            "github_repo_url": "https://github.com/yudakov21/order_payment_api",
            "assignment_description": "Analyze the code",
            "candidate_level": "Junior"
        }
        response = test_client.post("/review/", json=payload)
        print("Response content:", response.content)
        assert response.status_code == 200


def test_review_endpoint_invalid_input(test_client):
    # incorrect input
    payload = {
        "github_repo_url": "https://github.com/test/repo",
        # is missed assignment_description
        "candidate_level": "Junior"
    }
    response = test_client.post("/review/", json=payload)
    assert response.status_code == 422
