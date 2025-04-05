terraform {
  source = "../../modules/networking"
}

include {
  path = find_in_parent_folders()
}

inputs = {
  environment = "dev"
  region      = "us-east-1"
  vpc_cidr    = "10.0.0.0/16"
  
  public_subnet_cidrs = [
    "10.0.1.0/24",
    "10.0.2.0/24"
  ]
  
  private_subnet_cidrs = [
    "10.0.3.0/24",
    "10.0.4.0/24"
  ]
  
  availability_zones = [
    "us-east-1a",
    "us-east-1b"
  ]
} 