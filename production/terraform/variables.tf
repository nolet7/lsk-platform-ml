variable "aws_region" {
  type = string
  default = "us-east-1"
}

variable "artifact_bucket_name" {
  type = string
  description = "Globally unique, approved synthetic-only artifact bucket name."
  validation {
    condition = length(var.artifact_bucket_name) >= 3 && length(var.artifact_bucket_name) <= 63
    error_message = "Bucket name must be 3 to 63 characters."
  }
}
