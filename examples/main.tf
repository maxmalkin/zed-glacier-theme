terraform {
  required_version = ">= 1.6.0"
}

variable "environment" {
  type    = string
  default = "development"
}

variable "services" {
  type    = map(number)
  default = { api = 8080, worker = 9090 }
}

locals {
  enabled = true
  labels  = { for name, port in var.services : name => "${var.environment}:${port}" }
}

resource "terraform_data" "service" {
  for_each = var.services
  input = {
    name    = each.key
    port    = each.value
    label   = local.labels[each.key]
    enabled = local.enabled
  }
}

output "summary" {
  value = <<-EOT
    Environment: ${upper(var.environment)}
    Services: ${join(", ", keys(var.services))}
  EOT
}
