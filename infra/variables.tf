variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "backend_count" {
  description = "Number of backend ECS tasks"
  type        = number
  default     = 2
}

variable "frontend_count" {
  description = "Number of frontend ECS tasks"
  type        = number
  default     = 2
}
