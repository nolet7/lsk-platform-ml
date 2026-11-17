import pytest
from production.scripts.prepare_release import render

def test_requires_digest():
    with pytest.raises(ValueError):
        render("REPLACE_WITH_APPROVED_ECR_IMAGE_DIGEST", "example/api:latest")

def test_correct_digest():
    image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/lsk-platform-ml-prod-api@sha256:" + "a" * 64
    assert render("image: REPLACE_WITH_APPROVED_ECR_IMAGE_DIGEST", image) == "image: " + image

def test_rejects_missing_marker():
    with pytest.raises(ValueError):
        render("image: none", "123456789012.dkr.ecr.us-east-1.amazonaws.com/a@sha256:" + "a" * 64)
