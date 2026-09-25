@shopee_pages
Feature: Verificar as abas do Controle Vendas Shopee sem alterar dados

  @shopee_panel
  Scenario: Painel
    Given access to the web application '${{controle_vendas_shopee:web}}'
    When I open the "Painel" tab in Controle Vendas Shopee
    Then I should see the "Seu negócio em números" heading in Controle Vendas Shopee
    And I should see the "Vendas recentes" heading in Controle Vendas Shopee

  @shopee_sales
  Scenario: Vendas
    Given access to the web application '${{controle_vendas_shopee:web}}'
    When I open the "Vendas" tab in Controle Vendas Shopee
    Then I should see the "Histórico de vendas" heading in Controle Vendas Shopee

  @shopee_stock
  Scenario: Estoque
    Given access to the web application '${{controle_vendas_shopee:web}}'
    When I open the "Estoque" tab in Controle Vendas Shopee
    Then I should see the "Produtos e estoque" heading in Controle Vendas Shopee

  @shopee_investments
  Scenario: Investimentos
    Given access to the web application '${{controle_vendas_shopee:web}}'
    When I open the "Investimentos" tab in Controle Vendas Shopee
    Then I should see the "Investimentos do negócio" heading in Controle Vendas Shopee
