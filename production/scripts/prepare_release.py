"""Prepare immutable ECR-digest manifest; do not apply placeholder images."""
import argparse
from pathlib import Path
import re

DIGEST = re.compile(r"^[0-9]{12}\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com/[a-z0-9/_-]+@sha256:[a-f0-9]{64}$")

def render(template, image):
    if not DIGEST.fullmatch(image):
        raise ValueError("ECR image must use an immutable sha256 digest")
    marker = "REPLACE_WITH_APPROVED_ECR_IMAGE_DIGEST"
    if template.count(marker) != 1:
        raise ValueError("Expected exactly one placeholder in deployment")
    return template.replace(marker, image)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--input", default="production/k8s/serving.yaml")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    rendered = render(Path(args.input).read_text(), args.image)
    Path(args.output).write_text(rendered)

if __name__ == "__main__":
    main()
