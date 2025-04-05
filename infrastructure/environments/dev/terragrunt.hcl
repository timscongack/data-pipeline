include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../modules//storage"
}

inputs = {
  environment = "dev"
  bucket_name = "data-pipeline-dev"
} 