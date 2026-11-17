variable "project_name" {
  type    = string
  default = "lsk-platform-ml"
}
variable "environment" {
  type        = string
  description = "Approved isolated AWS account environment."
  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment must be dev, stage, or prod"
  }
}
variable "vpc_cidr" {
  type        = string
  description = "Unique VPC CIDR from networking team."
}
variable "kubernetes_version" {
  type        = string
  description = "Approved EKS-supported Kubernetes version."
}
variable "node_instance_types" {
  type        = list(string)
  description = "Approved general node family and size."
}
variable "eks_deployer_role_arn" {
  type        = string
  description = "Existing least-privileged role for deployment runner, distinct from Terraform provisioning role."
  validation {
    condition     = can(regex("^arn:aws:iam::[0-9]{12}:role/", var.eks_deployer_role_arn))
    error_message = "Must be an IAM role ARN."
  }
}

variable "eks_platform_admin_role_arn" {
  type        = string
  description = "Separate privileged cluster-bootstrap role, not used by CI deployer."
  validation {
    condition     = can(regex("^arn:aws:iam::[0-9]{12}:role/", var.eks_platform_admin_role_arn))
    error_message = "Must be an IAM role ARN."
  }
}
