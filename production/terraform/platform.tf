# EKS foundation for a single approved AWS environment/account.
# Apply only after external state backend, OIDC deployment principal, budget and threat-review approval.
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

locals {
  azs  = slice(data.aws_availability_zones.available.names, 0, 3)
  name = "${var.project_name}-${var.environment}"
  tags = {
    Project            = var.project_name
    Environment        = var.environment
    DataClassification = "synthetic-only"
    ManagedBy          = "terraform"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = local.name
  cidr = var.vpc_cidr
  azs  = local.azs

  private_subnets        = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 4, i)]
  public_subnets         = [for i, az in local.azs : cidrsubnet(var.vpc_cidr, 4, i + 8)]
  enable_nat_gateway     = true
  single_nat_gateway     = false
  one_nat_gateway_per_az = true
  enable_dns_hostnames   = true
  enable_dns_support     = true
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
  tags = local.tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.26.0"

  name                                     = local.name
  kubernetes_version                       = var.kubernetes_version
  endpoint_private_access                  = true
  endpoint_public_access                   = false
  enable_cluster_creator_admin_permissions = false

  enabled_log_types   = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  authentication_mode = "API"
  addons = {
    coredns                = {}
    kube-proxy             = {}
    vpc-cni                = { before_compute = true }
    eks-pod-identity-agent = { before_compute = true }
  }
  access_entries = {
    platform_deployer = {
      principal_arn = var.eks_deployer_role_arn
      policy_associations = {
        namespace_admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAdminPolicy"
          access_scope = { type = "namespace", namespaces = ["ml-quality"] }
        }
      }
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets
  eks_managed_node_groups = {
    general = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = var.node_instance_types
      min_size       = 3
      desired_size   = 3
      max_size       = 9
      capacity_type  = "ON_DEMAND"
      labels         = { workload = "api" }
    }
  }
  tags = local.tags
}

resource "aws_ecr_repository" "api" {
  name                 = "${local.name}-api"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
  tags = local.tags
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Retain last 30 production image tags"
      selection    = { tagStatus = "any", countType = "imageCountMoreThan", countNumber = 30 }
      action       = { type = "expire" }
    }]
  })
}
