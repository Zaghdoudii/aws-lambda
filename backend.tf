terraform {
  backend "s3" {
    bucket = "talan-com-tfstates-tti"
    key    = "tfstates/layers/talan-finops-pfe.tfstate"
    region = "eu-west-3"
  }
}