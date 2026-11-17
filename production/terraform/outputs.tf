output "cluster_name" {
  value = module.eks.cluster_name
}
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
  sensitive = true
}
output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}
output "artifact_bucket" {
  value = aws_s3_bucket.ml_artifacts.id
}
output "vpc_id" {
  value = module.vpc.vpc_id
}
output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
