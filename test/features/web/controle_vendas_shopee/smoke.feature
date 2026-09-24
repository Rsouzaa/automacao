@smoke
Feature: Controle Vendas Shopee smoke test

  Scenario: Dashboard is available
    Given access to the web application '${{controle_vendas_shopee:web}}'
    Then I should see the Controle Vendas Shopee dashboard
