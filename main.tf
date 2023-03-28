provider "aws" {
  region = "eu-west-1"
}

resource "aws_lambda_function" "lambda_finops" {
  function_name    = "lambda-gestion-couts"
  description      = "Function gestion couts"
  filename         = data.archive_file.lambda-finops-src.output_path
  source_code_hash = data.archive_file.lambda-finops-src.output_base64sha256
  role             = "arn:aws:iam::802617578034:role/role-talan-lambda-finops"
  handler          = "lambda_finops.lambda_handler"
  runtime          = "python3.9"
  timeout          = 500
  tags             = { "Name" = "lambda-gestion-couts" }

}

resource "null_resource" "install_lambda_dependencies" {
  provisioner "local-exec" {
    command = "pip install -r requirements.txt -t ${path.module}/functions/"
  }
}



