terraform {
  source = "../../../modules/storage"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  environment = "dev"
  region      = "us-east-1"
} 