# Configure the Azure provider
terraform {
  backend "azurerm" {
    resource_group_name  = "general"
    storage_account_name = "lvegeneralstorage01"
    container_name       = "tfstate"
    key                  = "prd.custom-chatgpt.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.62.0"
    }
    azuread = {
      version="~> 2.39.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 5.29"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "azuread" {}

provider "github" {
  owner = "Lukas1v"
}