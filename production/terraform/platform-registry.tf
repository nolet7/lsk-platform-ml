resource "aws_ecr_repository" "ml_platform_api" {
  name                 = "${local.name}-control-plane"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = local.tags
}
output "ml_platform_ecr_repository" {
  value = aws_ecr_repository.ml_platform_api.repository_url
}

resource "aws_ecr_repository" "ml_platform_worker" {
  name                 = "${local.name}-worker"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = local.tags
}
output "ml_platform_worker_ecr_repository" {
  value = aws_ecr_repository.ml_platform_worker.repository_url
}
