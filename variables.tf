variable "lambda-role-name" {
  description = "Set the role name that lambda will use"
  type        = string
}
variable "env" {
  type        = string
  description = "Environment to  witch you will deploy"
}
variable "vpc-name" {
  type        = string
  description = "The name of the account VPC"
}
