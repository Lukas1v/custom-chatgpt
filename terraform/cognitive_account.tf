resource "azurerm_cognitive_account" "cognitive_service" {
  name                = "custom-chatgpt-cognitive-services"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku_name            = "S0"
  kind                = "CognitiveServices"
}