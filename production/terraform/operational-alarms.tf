variable "monthly_budget_usd" {
  type        = number
  description = "Approved estimated monthly cost budget (not an enforceable cap)."
  validation {
    condition     = var.monthly_budget_usd > 0
    error_message = "Monthly budget must be positive."
  }
}
variable "budget_notification_emails" {
  type        = list(string)
  description = "Authorized FinOps notification addresses."
  validation {
    condition     = length(var.budget_notification_emails) > 0
    error_message = "At least one budget notification recipient required."
  }
}
variable "alarm_sns_topic_arn" {
  type        = string
  description = "Approved SNS alert topic with routed on-call subscriber."
  validation {
    condition     = can(regex("^arn:aws:sns:", var.alarm_sns_topic_arn))
    error_message = "Expected SNS topic ARN."
  }
}
resource "aws_budgets_budget" "platform" {
  name         = "${local.name}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = var.budget_notification_emails
  }
}
resource "aws_cloudwatch_metric_alarm" "db_cpu" {
  alarm_name          = "${local.name}-rds-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization above 80% for 15 minutes"
  dimensions          = { DBInstanceIdentifier = aws_db_instance.metadata.identifier }
  alarm_actions       = [var.alarm_sns_topic_arn]
  ok_actions          = [var.alarm_sns_topic_arn]
  treat_missing_data  = "missing"
}
resource "aws_cloudwatch_metric_alarm" "db_storage" {
  alarm_name          = "${local.name}-rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 21474836480
  alarm_description   = "RDS storage below 20GiB"
  dimensions          = { DBInstanceIdentifier = aws_db_instance.metadata.identifier }
  alarm_actions       = [var.alarm_sns_topic_arn]
  ok_actions          = [var.alarm_sns_topic_arn]
  treat_missing_data  = "missing"
}
