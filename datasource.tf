data "aws_caller_identity" "current" {}

data "archive_file" "lambda-finops-src" {
  type = "zip"
  source_dir = "functions/"
  output_path = "lambda-finops.zip"
}