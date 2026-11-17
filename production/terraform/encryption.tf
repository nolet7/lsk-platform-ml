resource "aws_kms_key" "ml" {
  description             = "Customer-managed encryption for ${local.name} metadata and model artifacts"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags                    = local.tags
}
resource "aws_kms_alias" "ml" {
  name          = "alias/${local.name}-data"
  target_key_id = aws_kms_key.ml.key_id
}
output "ml_kms_key_arn" {
  value = aws_kms_key.ml.arn
}
