variable "enable_gpu_nodes" {
  type        = bool
  default     = false
  description = "Cost-incurring GPU training node group, approved separately."
}
variable "gpu_instance_types" {
  type        = list(string)
  default     = ["g6.xlarge"]
  description = "GPU instance types approved for the selected AWS region."
}
variable "gpu_node_max" {
  type        = number
  default     = 4
  description = "Maximum GPU node count (requires autoscaler/controller)."
  validation {
    condition     = var.gpu_node_max >= 1 && var.gpu_node_max <= 10
    error_message = "GPU node limit must be within approved 1-10 bound."
  }
}
