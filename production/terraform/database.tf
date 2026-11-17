resource "aws_db_subnet_group" "ml" {
  name = "${local.name}-db"
  subnet_ids = module.vpc.private_subnets
  tags = local.tags
}
resource "aws_security_group" "database" {
  name_prefix = "${local.name}-db-"
  description = "RDS PostgreSQL access from EKS nodes"
  vpc_id = module.vpc.vpc_id
  tags = local.tags
  lifecycle { create_before_destroy = true }
}
resource "aws_vpc_security_group_ingress_rule" "postgres_from_nodes" {
  security_group_id = aws_security_group.database.id
  referenced_security_group_id = module.eks.node_security_group_id
  ip_protocol = "tcp"
  from_port = 5432
  to_port = 5432
}
resource "aws_db_instance" "metadata" {
  identifier = "${local.name}-metadata"
  engine = "postgres"
  instance_class = var.db_instance_class
  allocated_storage = 50
  max_allocated_storage = 200
  storage_type = "gp3"
  storage_encrypted = true
  db_name = "mlplatform"
  username = "mladmin"
  manage_master_user_password = true
  db_subnet_group_name = aws_db_subnet_group.ml.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible = false
  multi_az = true
  backup_retention_period = 14
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${local.name}-final-snapshot"
  auto_minor_version_upgrade = true
  copy_tags_to_snapshot = true
  tags = local.tags
}
variable "db_instance_class" {
  type = string
  description = "Approved metadata DB instance class."
}
output "database_endpoint" {
  value = aws_db_instance.metadata.address
  sensitive = true
}
