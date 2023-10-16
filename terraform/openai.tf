### Create the resource group
resource "azurerm_resource_group" "rg" {
  name     = "custom-chatgpt-prd"
  location = "westeurope"

  tags = {
    app = "custom-chatgpt"
    env = "PRD"
  }
}

### Azure Open AI Account
resource "azurerm_cognitive_account" "openai" {
  name                          = "custom-chatgpt-openai"
  location                      = "westeurope"
  resource_group_name           = azurerm_resource_group.rg.name
  kind                          = "OpenAI"
  custom_subdomain_name         = "lve-custom-chatgpt"
  sku_name                      = "S0" #S0
  public_network_access_enabled = true #change to false
  identity {
    type = "SystemAssigned"
  }

  tags = {
    app = "custom-chatgpt"
    env = "PRD"
  }
}

### Azure Open AI Model - Chat GPT
resource "azurerm_cognitive_deployment" "chatgpt_model" {
  name                 = "custom-chatgpt-model"
  cognitive_account_id = resource.azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "gpt-35-turbo"
    version = "0301"
  }

  scale {
    type = "Standard"
  }
}

### Azure Open AI Model - Embeddings
resource "azurerm_cognitive_deployment" "embeddings_model" {
  name                 = "embeddings-model"
  cognitive_account_id = resource.azurerm_cognitive_account.openai.id
  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  scale {
    type = "Standard"
  }
}