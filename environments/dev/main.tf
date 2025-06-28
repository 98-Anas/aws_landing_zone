module "networking" {
  source              = "../modules/networking"
  aws_region          = var.aws_region
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
}


module "compute" {
  source             = "../modules/compute"
  vpc_id             = module.networking.vpc_id
  public_subnet_ids  = module.networking.public_subnet_ids
  environment        = var.environment
  instance_count     = 1 # Free tier allows 750 hours/month of t2.micro
}

module "logging" {
  source      = "../modules/logging"
  vpc_id      = module.networking.vpc_id
  environment = var.environment
}